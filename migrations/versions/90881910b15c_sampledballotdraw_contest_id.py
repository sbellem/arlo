# pylint: disable=invalid-name
"""SampledBallotDraw.contest_id

Revision ID: 90881910b15c
Revises:
Create Date: 2020-07-06 23:24:27.444706+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "90881910b15c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sampled_ballot_draw",
        sa.Column("contest_id", sa.String(length=200), nullable=False),
    )
    op.create_foreign_key(
        op.f("sampled_ballot_draw_contest_id_fkey"),
        "sampled_ballot_draw",
        "contest",
        ["contest_id"],
        ["id"],
        ondelete="cascade",
    )
    op.drop_constraint(op.f("sampled_ballot_draw_pkey"), "sampled_ballot_draw")
    op.create_primary_key(
        op.f("sampled_ballot_draw_pkey"),
        "sampled_ballot_draw",
        ["ballot_id", "round_id", "contest_id", "ticket_number"],
    )


def downgrade():
    op.drop_constraint(op.f("sampled_ballot_draw_pkey"), "sampled_ballot_draw")
    op.create_primary_key(
        op.f("sampled_ballot_draw_pkey"),
        "sampled_ballot_draw",
        ["ballot_id", "round_id", "ticket_number"],
    )
    op.drop_constraint(
        op.f("sampled_ballot_draw_contest_id_fkey"),
        "sampled_ballot_draw",
        type_="foreignkey",
    )
    op.drop_column("sampled_ballot_draw", "contest_id")
