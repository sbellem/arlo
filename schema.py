from graphene import Boolean, DateTime, Enum, Field, ID, List, ObjectType, Int, Mutation, String, Schema
import uuid

def build(db, models):
    class Vote(Enum):
        YES = 'YES'
        NO = 'NO'
        NO_CONCENSUS = 'NO_CONCENSUS'
        NO_VOTE = 'NO_VOTE'

    class Ballot(ObjectType):
        # round = Field(Round)
        # jurisdiction = Field(Jurisdiction)
        # batch = Field(Batch)
        ballot_position = Int(required=True)
        times_sampled = Int(required=True)
        vote = Field(Vote)
        comment = String()

    class Choice(ObjectType):
        id = ID(required=True)
        name = String()
        num_votes = Int()

    class Contest(ObjectType):
        id = ID(required=True)
        name = String()
        choices = List(Choice)
        total_ballots_cast = Int()
        num_winners = Int()

        @staticmethod
        def resolve_choices(contest, info):
            choices = models.TargetedContestChoice.query.filter_by(contest_id=contest.id)
            return [
                Choice(
                    id=choice.id,
                    name=choice.name,
                    num_votes=choice.num_votes
                )
                for choice in choices
            ]

    class Result(ObjectType):
        result = Int()

    class Choice(ObjectType):
        id = ID(required=True)
        name = String(required=True)
        num_votes = Int(required=True)
        results = List(Result, required=True)

    class Contest(ObjectType):
        id = ID(required=True)
        name = String(required=True)
        total_ballots_cast = Int(required=True)
        num_winners = Int(required=True)
        choices = List(Choice, required=True)
        results = List(Result, required=True)

    class Affiliation(Enum):
        NONE = ''
        INDEPENDENT = 'IND'
        DEMOCRAT = 'DEM'
        REPUBLICAN = 'REP'
        LIBERTARIAN = 'LIB'

    class AuditBoardMember(ObjectType):
        id = ID(required=True)
        name = String(required=True)
        affiliation = Field(Affiliation)

    class AuditBoard(ObjectType):
        id = ID(required=True)
        name = String()
        members = List(AuditBoardMember)

    class BallotManifest(ObjectType):
        manifest = String(required=True)
        filename = String(required=True)
        uploaded_at = DateTime(required=True)
        num_ballots = Int(required=True)
        num_batches = Int(required=True)

    class Batch(ObjectType):
        id = ID(required=True)
        name = String(required=True)
        num_ballots = Int(required=True)
        storage_location = String(required=True)
        tabulator = String(required=True)
        ballots = List(Ballot)

    class Jurisdiction(ObjectType):
        id = ID(required=True)
        name = String()
        contests = List(Contest)
        audit_boards = List(AuditBoard)
        ballot_manifest = Field(BallotManifest)
        batches = List(Batch)

    class Election(ObjectType):
        id = ID(required=True)
        name = String()
        risk_limit = Int(description="Audit risk limit percentage, e.g. 5 = 5%")
        random_seed = String(description="Seeds the pseudo-random number generator")
        contests = List(Contest)
        jurisdictions = List(Jurisdiction)
        contest = Field(Contest, id=ID())

        @staticmethod
        def resolve_contests(election, info):
            contests = models.TargetedContest.query.filter_by(election_id=election.id).all()
            return [
                Contest(
                    id=contest.id,
                    name=contest.name,
                    total_ballots_cast=contest.total_ballots_cast,
                    num_winners=contest.num_winners
                )
                for contest in contests
            ]

        @staticmethod
        def resolve_contest(election, info, id):
            contest = models.TargetedContest.query.filter_by(election_id=election.id, id=id).one()
            return Contest(
                id=contest.id,
                name=contest.name,
                total_ballots_cast=contest.total_ballots_cast,
                num_winners=contest.num_winners
            )

        @staticmethod
        def resolve_jurisdictions(election, info):
            jurisdictions = models.Jurisdiction.query.filter_by(election_id=election.id).all()
            return [
                Jurisdiction(
                    id=jurisdiction.id,
                    name=jurisdiction.name,
                    ballot_manifest=None if not jurisdiction.manifest else BallotManifest(
                        manifest=jurisdiction.manifest,
                        filename=jurisdiction.manifest_filename,
                        uploaded_at=jurisdiction.manifest_uploaded_at,
                        num_ballots=jurisdiction.manifest_num_ballots,
                        num_batches=jurisdiction.manifest_num_batches
                    )
                )
                for jurisdiction in jurisdictions
            ]

    class Query(ObjectType):
        elections = List(Election)
        election = Field(Election, id=ID())

        @staticmethod
        def resolve_elections(root, info):
            elections = models.Election.query.all()
            return [
                Election(
                    id=election.id,
                    name=election.name,
                    risk_limit=election.risk_limit
                )
                for election in elections
            ]

        @staticmethod
        def resolve_election(root, info, id):
            election = models.Election.query.filter_by(id=id).one()
            return Election(id=id, name=election.name, risk_limit=election.risk_limit)

    class RecordBallot(Mutation):
        class Arguments:
            election_id = ID(required=True)
            jurisdiction_id = ID(required=True)
            batch_id = ID(required=True)
            ballot_id = ID(required=True)
            vote = Vote()
            comment = String()

        ok = Boolean()
        ballot = Field(Ballot)

        @staticmethod
        def mutate(root, info, election_id, jurisdiction_id, batch_id, ballot_id, vote, comment):
            ballots = models.SampledBallot \
                .query.filter_by(jurisdiction_id=jurisdiction_id, batch_id=batch_id, ballot_position=ballot_position) \
                .join(Round).filter_by(election_id=election_id, id=round_id) \
                .all()

    class CreateElection(Mutation):
        class Arguments:
            election_id = ID()

        ok = Boolean(required=True)
        election_id = ID(required=True)

        @staticmethod
        def mutate(root, info, election_id=None):
            e = models.Election(id=election_id or str(uuid.uuid4()), name="")
            db.session.add(e)
            db.session.commit()
            return CreateElection(ok=True, election_id=election_id)

    class Mutations(ObjectType):
        record_ballot = RecordBallot.Field()
        create_election = CreateElection.Field()

    return Schema(query=Query, mutation=Mutations)
