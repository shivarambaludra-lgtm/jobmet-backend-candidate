"""add AI fields to applications table

Revision ID: 002_add_ai_fields
Revises: 001_initial_migration
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_add_ai_fields'
down_revision = '68dde98cb1c4'  # Updated to match initial migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add AI-related columns to applications table"""
    
    # Add match_score column
    op.add_column('applications',
        sa.Column('match_score', sa.Float(), nullable=True,
                  comment='AI-generated match score (0-100)')
    )
    
    # Add strengths column (JSON array)
    op.add_column('applications',
        sa.Column('strengths', postgresql.JSON(astext_type=sa.Text()), nullable=True,
                  comment='List of candidate strengths identified by AI')
    )
    
    # Add gaps column (JSON array)
    op.add_column('applications',
        sa.Column('gaps', postgresql.JSON(astext_type=sa.Text()), nullable=True,
                  comment='List of skill/experience gaps identified by AI')
    )
    
    # Add key_skills_matched column (JSON array)
    op.add_column('applications',
        sa.Column('key_skills_matched', postgresql.JSON(astext_type=sa.Text()), nullable=True,
                  comment='Required skills that candidate possesses')
    )
    
    # Add ai_reasoning column
    op.add_column('applications',
        sa.Column('ai_reasoning', sa.Text(), nullable=True,
                  comment='AI explanation for the match score and recommendation')
    )
    
    # Add applied_at timestamp
    op.add_column('applications',
        sa.Column('applied_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()'),
                  comment='When the application was submitted')
    )
    
    # Add updated_at timestamp
    op.add_column('applications',
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()'),
                  comment='Last update timestamp')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_applications_candidate_id', 'applications', ['candidate_id'])
    op.create_index('ix_applications_job_id', 'applications', ['job_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])
    op.create_index('ix_applications_match_score', 'applications', ['match_score'])


def downgrade() -> None:
    """Remove AI-related columns from applications table"""
    
    # Drop indexes
    op.drop_index('ix_applications_match_score', table_name='applications')
    op.drop_index('ix_applications_status', table_name='applications')
    op.drop_index('ix_applications_job_id', table_name='applications')
    op.drop_index('ix_applications_candidate_id', table_name='applications')
    
    # Drop columns
    op.drop_column('applications', 'updated_at')
    op.drop_column('applications', 'applied_at')
    op.drop_column('applications', 'ai_reasoning')
    op.drop_column('applications', 'key_skills_matched')
    op.drop_column('applications', 'gaps')
    op.drop_column('applications', 'strengths')
    op.drop_column('applications', 'match_score')
