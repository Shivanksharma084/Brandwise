"""Initial schema with multi-tenancy, RBAC, guidelines, facts, findings, and RLS

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 1. Tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id', name='pk_tenants')
    )
    op.create_index('ix_tenants_id', 'tenants', ['id'], unique=False)
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)

    # 2. Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id', name='pk_roles')
    )
    op.create_index('ix_roles_id', 'roles', ['id'], unique=False)
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)

    # 3. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('role_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_users_role_id_roles'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_users_tenant_id_tenants', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_users')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'], unique=False)

    # 4. Brand Workspaces table
    op.create_table(
        'brand_workspaces',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='fk_brand_workspaces_tenant_id_tenants', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_brand_workspaces')
    )
    op.create_index('ix_brand_workspaces_id', 'brand_workspaces', ['id'], unique=False)
    op.create_index('ix_brand_workspaces_tenant_id', 'brand_workspaces', ['tenant_id'], unique=False)

    # 5. Guideline Documents table
    op.create_table(
        'guideline_documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['brand_workspaces.id'], name='fk_guideline_documents_workspace_id_brand_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_guideline_documents')
    )
    op.create_index('ix_guideline_documents_id', 'guideline_documents', ['id'], unique=False)
    op.create_index('ix_guideline_documents_tenant_id', 'guideline_documents', ['tenant_id'], unique=False)
    op.create_index('ix_guideline_documents_workspace_id', 'guideline_documents', ['workspace_id'], unique=False)

    # 6. Guideline Rules table (atomic rules with pgvector)
    op.create_table(
        'guideline_rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('clause_ref', sa.String(length=50), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('channels', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['guideline_documents.id'], name='fk_guideline_rules_document_id_guideline_documents', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_guideline_rules')
    )
    op.create_index('ix_guideline_rules_id', 'guideline_rules', ['id'], unique=False)
    op.create_index('ix_guideline_rules_tenant_id', 'guideline_rules', ['tenant_id'], unique=False)
    op.create_index('ix_guideline_rules_document_id', 'guideline_rules', ['document_id'], unique=False)

    # 7. Fact Records table (with pgvector)
    op.create_table(
        'fact_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('statistic', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('owner', sa.String(length=255), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['brand_workspaces.id'], name='fk_fact_records_workspace_id_brand_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_fact_records')
    )
    op.create_index('ix_fact_records_id', 'fact_records', ['id'], unique=False)
    op.create_index('ix_fact_records_tenant_id', 'fact_records', ['tenant_id'], unique=False)
    op.create_index('ix_fact_records_workspace_id', 'fact_records', ['workspace_id'], unique=False)

    # 8. Terminology Entries table
    op.create_table(
        'terminology_entries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('term', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('preferred_alternative', sa.String(length=100), nullable=True),
        sa.Column('examples', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['brand_workspaces.id'], name='fk_terminology_entries_workspace_id_brand_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_terminology_entries')
    )
    op.create_index('ix_terminology_entries_id', 'terminology_entries', ['id'], unique=False)
    op.create_index('ix_terminology_entries_tenant_id', 'terminology_entries', ['tenant_id'], unique=False)
    op.create_index('ix_terminology_entries_term', 'terminology_entries', ['term'], unique=False)
    op.create_index('ix_terminology_entries_workspace_id', 'terminology_entries', ['workspace_id'], unique=False)

    # 9. Assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['workspace_id'], ['brand_workspaces.id'], name='fk_assets_workspace_id_brand_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_assets')
    )
    op.create_index('ix_assets_id', 'assets', ['id'], unique=False)
    op.create_index('ix_assets_tenant_id', 'assets', ['tenant_id'], unique=False)
    op.create_index('ix_assets_workspace_id', 'assets', ['workspace_id'], unique=False)

    # 10. Content Submissions table
    op.create_table(
        'content_submissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('creator_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('channel', sa.String(length=50), nullable=True),
        sa.Column('campaign', sa.String(length=100), nullable=True),
        sa.Column('is_ai_assisted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], name='fk_content_submissions_creator_id_users', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['brand_workspaces.id'], name='fk_content_submissions_workspace_id_brand_workspaces', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_content_submissions')
    )
    op.create_index('ix_content_submissions_id', 'content_submissions', ['id'], unique=False)
    op.create_index('ix_content_submissions_tenant_id', 'content_submissions', ['tenant_id'], unique=False)
    op.create_index('ix_content_submissions_creator_id', 'content_submissions', ['creator_id'], unique=False)
    op.create_index('ix_content_submissions_workspace_id', 'content_submissions', ['workspace_id'], unique=False)

    # 11. Review Findings table
    op.create_table(
        'review_findings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('submission_id', sa.UUID(), nullable=False),
        sa.Column('rule_id', sa.UUID(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('span_start', sa.Integer(), nullable=True),
        sa.Column('span_end', sa.Integer(), nullable=True),
        sa.Column('highlighted_text', sa.Text(), nullable=True),
        sa.Column('region_box', sa.JSON(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('source_ref', sa.String(length=255), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('suggested_fix', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
        sa.Column('guideline_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['rule_id'], ['guideline_rules.id'], name='fk_review_findings_rule_id_guideline_rules', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['submission_id'], ['content_submissions.id'], name='fk_review_findings_submission_id_content_submissions', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_review_findings')
    )
    op.create_index('ix_review_findings_id', 'review_findings', ['id'], unique=False)
    op.create_index('ix_review_findings_tenant_id', 'review_findings', ['tenant_id'], unique=False)
    op.create_index('ix_review_findings_submission_id', 'review_findings', ['submission_id'], unique=False)
    op.create_index('ix_review_findings_rule_id', 'review_findings', ['rule_id'], unique=False)

    # 12. Workflow States table
    op.create_table(
        'workflow_states',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('submission_id', sa.UUID(), nullable=False),
        sa.Column('from_state', sa.String(length=50), nullable=False),
        sa.Column('to_state', sa.String(length=50), nullable=False),
        sa.Column('transition_by', sa.UUID(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['submission_id'], ['content_submissions.id'], name='fk_workflow_states_submission_id_content_submissions', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transition_by'], ['users.id'], name='fk_workflow_states_transition_by_users'),
        sa.PrimaryKeyConstraint('id', name='pk_workflow_states')
    )
    op.create_index('ix_workflow_states_id', 'workflow_states', ['id'], unique=False)
    op.create_index('ix_workflow_states_tenant_id', 'workflow_states', ['tenant_id'], unique=False)
    op.create_index('ix_workflow_states_submission_id', 'workflow_states', ['submission_id'], unique=False)

    # 13. Comments table
    op.create_table(
        'comments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('submission_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id'], name='fk_comments_parent_id_comments', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submission_id'], ['content_submissions.id'], name='fk_comments_submission_id_content_submissions', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_comments_user_id_users', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_comments')
    )
    op.create_index('ix_comments_id', 'comments', ['id'], unique=False)
    op.create_index('ix_comments_tenant_id', 'comments', ['tenant_id'], unique=False)
    op.create_index('ix_comments_submission_id', 'comments', ['submission_id'], unique=False)

    # 14. Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_audit_logs_user_id_users', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='pk_audit_logs')
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'], unique=False)
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'], unique=False)
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)

    # 15. Approval Overrides table
    op.create_table(
        'approval_overrides',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('finding_id', sa.UUID(), nullable=False),
        sa.Column('approver_id', sa.UUID(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], name='fk_approval_overrides_approver_id_users'),
        sa.ForeignKeyConstraint(['finding_id'], ['review_findings.id'], name='fk_approval_overrides_finding_id_review_findings', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_approval_overrides')
    )
    op.create_index('ix_approval_overrides_id', 'approval_overrides', ['id'], unique=False)
    op.create_index('ix_approval_overrides_tenant_id', 'approval_overrides', ['tenant_id'], unique=False)
    op.create_index('ix_approval_overrides_finding_id', 'approval_overrides', ['finding_id'], unique=False)

    # 16. Insight Metrics table
    op.create_table(
        'insight_metrics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('metric_type', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('dimensions', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id', name='pk_insight_metrics')
    )
    op.create_index('ix_insight_metrics_id', 'insight_metrics', ['id'], unique=False)
    op.create_index('ix_insight_metrics_tenant_id', 'insight_metrics', ['tenant_id'], unique=False)

    # 17. Guideline Gaps table
    op.create_table(
        'guideline_gaps',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('rule_id', sa.UUID(), nullable=False),
        sa.Column('override_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('dispute_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('recurring_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('suggested_clarification', sa.Text(), nullable=False),
        sa.Column('example_cases', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['rule_id'], ['guideline_rules.id'], name='fk_guideline_gaps_rule_id_guideline_rules', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_guideline_gaps')
    )
    op.create_index('ix_guideline_gaps_id', 'guideline_gaps', ['id'], unique=False)
    op.create_index('ix_guideline_gaps_tenant_id', 'guideline_gaps', ['tenant_id'], unique=False)
    op.create_index('ix_guideline_gaps_rule_id', 'guideline_gaps', ['rule_id'], unique=False)

    # 18. Row-Level Security (RLS) policies
    # Enable RLS on all tenant-isolated tables
    tables = [
        'brand_workspaces',
        'guideline_documents',
        'guideline_rules',
        'fact_records',
        'terminology_entries',
        'assets',
        'content_submissions',
        'review_findings',
        'workflow_states',
        'comments',
        'audit_logs',
        'approval_overrides',
        'insight_metrics',
        'guideline_gaps'
    ]
    for table in tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(
            f"CREATE POLICY tenant_isolation_policy ON {table} "
            f"USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);"
        )


def downgrade() -> None:
    tables = [
        'guideline_gaps',
        'insight_metrics',
        'approval_overrides',
        'audit_logs',
        'comments',
        'workflow_states',
        'review_findings',
        'content_submissions',
        'assets',
        'terminology_entries',
        'fact_records',
        'guideline_rules',
        'guideline_documents',
        'brand_workspaces',
        'users',
        'roles',
        'tenants'
    ]
    for table in tables:
        op.drop_table(table)
    op.execute("DROP EXTENSION IF EXISTS vector")
