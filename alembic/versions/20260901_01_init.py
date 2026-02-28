"""initial schema with postgis entities"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision = "20260901_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "boundaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("geom", Geometry(geometry_type="POLYGON", srid=4326), nullable=False),
    )
    op.create_index("ix_boundaries_name", "boundaries", ["name"], unique=True)

    op.create_table(
        "signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("extracted_location_text", sa.String(length=500), nullable=True),
        sa.Column("features", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_signals_source_type", "signals", ["source_type"])
    op.create_index("ix_signals_source_id", "signals", ["source_id"])
    op.create_index("ix_signals_observed_at", "signals", ["observed_at"])

    op.create_table(
        "incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("score_breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("centroid", Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_incidents_first_seen", "incidents", ["first_seen"])
    op.create_index("ix_incidents_last_seen", "incidents", ["last_seen"])
    op.create_index("ix_incidents_confidence_score", "incidents", ["confidence_score"])

    op.create_table(
        "incident_signals",
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("signal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signals.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("linked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "incident_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_incident_feedback_incident_id", "incident_feedback", ["incident_id"])


def downgrade() -> None:
    op.drop_index("ix_incident_feedback_incident_id", table_name="incident_feedback")
    op.drop_table("incident_feedback")
    op.drop_table("incident_signals")
    op.drop_index("ix_incidents_confidence_score", table_name="incidents")
    op.drop_index("ix_incidents_last_seen", table_name="incidents")
    op.drop_index("ix_incidents_first_seen", table_name="incidents")
    op.drop_table("incidents")
    op.drop_index("ix_signals_observed_at", table_name="signals")
    op.drop_index("ix_signals_source_id", table_name="signals")
    op.drop_index("ix_signals_source_type", table_name="signals")
    op.drop_table("signals")
    op.drop_index("ix_boundaries_name", table_name="boundaries")
    op.drop_table("boundaries")
