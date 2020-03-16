# type: ignore
from sqlalchemy.orm import relationship, backref
from typing import Union, List
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# on-delete-cascade is done in SQLAlchemy like this:
# https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete


class Organization(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    elections = relationship("Election", backref="organization", passive_deletes=True)


class Election(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    election_date = db.Column(db.Date, nullable=True)
    election_type = db.Column(db.String(200), nullable=True)
    meeting_date = db.Column(db.Date, nullable=True)
    risk_limit = db.Column(db.Integer, nullable=True)
    random_seed = db.Column(db.String(100), nullable=True)

    # an election is "online" if every ballot is entered online, vs. offline in a tally sheet.
    online = db.Column(db.Boolean, nullable=False, default=False)

    # Who does this election belong to?
    organization_id = db.Column(
        db.String(200),
        db.ForeignKey("organization.id", ondelete="cascade"),
        nullable=True,
    )

    frozen_at = db.Column(db.DateTime(timezone=False), nullable=True)

    jurisdictions = relationship(
        "Jurisdiction", backref="election", passive_deletes=True
    )
    contests = relationship("Contest", backref="election", passive_deletes=True)
    rounds = relationship("Round", backref="election", passive_deletes=True)

    jurisdictions_file = db.Column(db.Text, nullable=True)
    jurisdictions_filename = db.Column(db.String(250), nullable=True)
    jurisdictions_file_uploaded_at = db.Column(
        db.DateTime(timezone=False), nullable=True
    )


# these are typically counties
class Jurisdiction(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    election_id = db.Column(
        db.String(200), db.ForeignKey("election.id", ondelete="cascade"), nullable=False
    )
    name = db.Column(db.String(200), nullable=False)
    manifest = db.Column(db.Text, nullable=True)
    manifest_filename = db.Column(db.String(250), nullable=True)
    manifest_uploaded_at = db.Column(db.DateTime(timezone=False), nullable=True)
    manifest_num_ballots = db.Column(db.Integer)
    manifest_num_batches = db.Column(db.Integer)

    # any error in the upload? null == none
    manifest_errors = db.Column(db.Text, nullable=True)

    # a JSON array of field names that are included in the CSV
    manifest_fields = db.Column(db.Text, nullable=True)

    batches = relationship("Batch", backref="jurisdiction", passive_deletes=True)
    audit_boards = relationship(
        "AuditBoard", backref="jurisdiction", passive_deletes=True
    )
    contests = relationship(
        "ContestJurisdiction", backref="jurisdiction", passive_deletes=True
    )


class User(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    external_id = db.Column(db.String(200), unique=True, nullable=True)

    organizations = relationship("Organization", secondary="audit_administration")
    jurisdictions = relationship(
        "Jurisdiction", secondary="jurisdiction_administration"
    )


class AuditAdministration(db.Model):
    organization_id = db.Column(
        db.String(200),
        db.ForeignKey("organization.id", ondelete="cascade"),
        nullable=False,
    )
    user_id = db.Column(
        db.String(200), db.ForeignKey("user.id", ondelete="cascade"), nullable=False
    )

    organization = relationship(
        Organization,
        backref=backref("audit_administrations", cascade="all, delete-orphan"),
    )
    user = relationship(
        User, backref=backref("audit_administrations", cascade="all, delete-orphan")
    )

    __table_args__ = (db.PrimaryKeyConstraint("organization_id", "user_id"),)


class JurisdictionAdministration(db.Model):
    user_id = db.Column(
        db.String(200), db.ForeignKey("user.id", ondelete="cascade"), nullable=False
    )
    jurisdiction_id = db.Column(
        db.String(200),
        db.ForeignKey("jurisdiction.id", ondelete="cascade"),
        nullable=True,
    )

    jurisdiction = relationship(
        Jurisdiction,
        backref=backref("jurisdiction_administrations", cascade="all, delete-orphan"),
    )
    user = relationship(
        User,
        backref=backref("jurisdiction_administrations", cascade="all, delete-orphan"),
    )

    __table_args__ = (db.PrimaryKeyConstraint("user_id", "jurisdiction_id"),)


class Batch(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    jurisdiction_id = db.Column(
        db.String(200),
        db.ForeignKey("jurisdiction.id", ondelete="cascade"),
        nullable=False,
    )
    name = db.Column(db.String(200), nullable=False)
    num_ballots = db.Column(db.Integer, nullable=False)
    storage_location = db.Column(db.String(200), nullable=True)
    tabulator = db.Column(db.String(200), nullable=True)

    ballots = relationship("SampledBallot", backref="batch", passive_deletes=True)
    ballot_draws = relationship(
        "SampledBallotDraw", backref="batch", passive_deletes=True
    )


class Contest(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    election_id = db.Column(
        db.String(200), db.ForeignKey("election.id", ondelete="cascade"), nullable=False
    )
    name = db.Column(db.String(200), nullable=False)
    # is_targeted = True for targeted contests, False for opportunistic contests
    is_targeted = db.Column(db.Boolean, nullable=False)
    total_ballots_cast = db.Column(db.Integer, nullable=False)
    num_winners = db.Column(db.Integer, nullable=False)
    votes_allowed = db.Column(db.Integer, nullable=False)

    choices = relationship("ContestChoice", backref="contest", passive_deletes=True)
    results = relationship(
        "RoundContestResult", backref="contest", passive_deletes=True
    )


class ContestChoice(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    contest_id = db.Column(
        db.String(200), db.ForeignKey("contest.id", ondelete="cascade"), nullable=False,
    )
    name = db.Column(db.String(200), nullable=False)
    num_votes = db.Column(db.Integer, nullable=False)

    results = relationship(
        "RoundContestResult", backref="contest_choice", passive_deletes=True
    )


class ContestJurisdiction(db.Model):
    contest_id = db.Column(
        db.String(200), db.ForeignKey("contest.id", ondelete="cascade"), nullable=False,
    )
    jurisdiction_id = db.Column(
        db.String(200),
        db.ForeignKey("jurisdiction.id", ondelete="cascade"),
        nullable=False,
    )

    __table_args__ = (db.PrimaryKeyConstraint("contest_id", "jurisdiction_id"),)


class AuditBoard(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    jurisdiction_id = db.Column(
        db.String(200),
        db.ForeignKey("jurisdiction.id", ondelete="cascade"),
        nullable=False,
    )
    name = db.Column(db.String(200))
    member_1 = db.Column(db.String(200), nullable=True)
    member_1_affiliation = db.Column(db.String(200), nullable=True)
    member_2 = db.Column(db.String(200), nullable=True)
    member_2_affiliation = db.Column(db.String(200), nullable=True)
    passphrase = db.Column(db.String(1000), unique=True, nullable=True)

    sampled_ballots = relationship(
        "SampledBallot", backref="audit_board", passive_deletes=True
    )


class Round(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    election_id = db.Column(
        db.String(200), db.ForeignKey("election.id", ondelete="cascade"), nullable=False
    )
    round_num = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint("election_id", "round_num"),)

    round_contests = relationship("RoundContest", backref="round", passive_deletes=True)
    sampled_ballot_draws = relationship(
        "SampledBallotDraw", backref="round", passive_deletes=True
    )


class SampledBallot(db.Model):
    batch_id = db.Column(
        db.String(200), db.ForeignKey("batch.id", ondelete="cascade"), nullable=False
    )

    # this ballot position should be 1-indexed
    ballot_position = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.PrimaryKeyConstraint("batch_id", "ballot_position"),)

    draws = relationship(
        "SampledBallotDraw", backref="sampled_ballot", passive_deletes=True
    )

    audit_board_id = db.Column(
        db.String(200),
        db.ForeignKey("audit_board.id", ondelete="cascade"),
        nullable=False,
    )
    vote = db.Column(db.String(200), nullable=True)
    comment = db.Column(db.Text, nullable=True)


class SampledBallotDraw(db.Model):
    batch_id = db.Column(
        db.String(200), db.ForeignKey("batch.id", ondelete="cascade"), nullable=False
    )
    ballot_position = db.Column(db.Integer, nullable=False)

    round_id = db.Column(
        db.String(200), db.ForeignKey("round.id", ondelete="cascade"), nullable=False
    )
    ticket_number = db.Column(db.String(200), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            "batch_id", "ballot_position", "round_id", "ticket_number"
        ),
        db.ForeignKeyConstraint(
            ["batch_id", "ballot_position"],
            ["sampled_ballot.batch_id", "sampled_ballot.ballot_position"],
            ondelete="cascade",
        ),
    )


class RoundContest(db.Model):
    round_id = db.Column(
        db.String(200), db.ForeignKey("round.id", ondelete="cascade"), nullable=False
    )
    contest_id = db.Column(
        db.String(200), db.ForeignKey("contest.id", ondelete="cascade"), nullable=False,
    )

    sample_size_options = db.Column(db.String(1000), nullable=True)

    results = relationship(
        "RoundContestResult", backref="round_contest", passive_deletes=True
    )

    __table_args__ = (db.PrimaryKeyConstraint("round_id", "contest_id"),)

    end_p_value = db.Column(db.Float)
    is_complete = db.Column(db.Boolean)
    sample_size = db.Column(db.Integer)


class RoundContestResult(db.Model):
    round_id = db.Column(
        db.String(200), db.ForeignKey("round.id", ondelete="cascade"), nullable=False
    )
    contest_id = db.Column(
        db.String(200), db.ForeignKey("contest.id", ondelete="cascade"), nullable=False,
    )
    __table_args__ = (
        db.PrimaryKeyConstraint("round_id", "contest_choice_id"),
        db.ForeignKeyConstraint(
            ["round_id", "contest_id"],
            ["round_contest.round_id", "round_contest.contest_id"],
            ondelete="cascade",
        ),
    )

    contest_choice_id = db.Column(
        db.String(200),
        db.ForeignKey("contest_choice.id", ondelete="cascade"),
        nullable=False,
    )
    result = db.Column(db.Integer)