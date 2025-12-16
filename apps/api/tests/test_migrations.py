"""
Integration tests for Alembic database migrations.

Tests verify that migrations can be applied and rolled back successfully.
This ensures production rollback procedures work correctly in case of issues.
"""
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session


@pytest.fixture
def alembic_config():
    """Create Alembic configuration for testing."""
    config = Config("alembic.ini")
    return config


@pytest.fixture
def test_engine(test_database_url):
    """Create test database engine for migration testing."""
    engine = create_engine(test_database_url)
    yield engine
    engine.dispose()


class TestSectionPatternsMigration:
    """Test section_patterns column migration (Medium Priority Issue #7)."""

    def test_upgrade_adds_section_patterns_column(self, alembic_config, test_engine):
        """Should add section_patterns column to workflows table."""
        # Arrange: Start from previous migration
        command.downgrade(alembic_config, "c3d4e5f6g7h9")

        # Act: Run upgrade to add section_patterns
        command.upgrade(alembic_config, "d4e5f6g7h8i0")

        # Assert: Verify column exists
        inspector = inspect(test_engine)
        columns = [col["name"] for col in inspector.get_columns("workflows")]
        assert "section_patterns" in columns

        # Verify column is nullable (backward compatible)
        column_info = next(
            col for col in inspector.get_columns("workflows")
            if col["name"] == "section_patterns"
        )
        assert column_info["nullable"] is True

    def test_downgrade_removes_section_patterns_column(self, alembic_config, test_engine):
        """Should remove section_patterns column when rolling back."""
        # Arrange: Start from current migration
        command.upgrade(alembic_config, "d4e5f6g7h8i0")

        # Act: Downgrade to previous migration
        command.downgrade(alembic_config, "c3d4e5f6g7h9")

        # Assert: Verify column is removed
        inspector = inspect(test_engine)
        columns = [col["name"] for col in inspector.get_columns("workflows")]
        assert "section_patterns" not in columns

    def test_upgrade_downgrade_cycle_preserves_data(self, alembic_config, test_engine):
        """Should preserve existing workflow data during upgrade/downgrade cycle."""
        # Arrange: Start from previous migration and insert test data
        command.downgrade(alembic_config, "c3d4e5f6g7h9")

        with Session(test_engine) as session:
            # Insert test workflow
            session.execute(text("""
                INSERT INTO workflows (id, organization_id, name, created_at, updated_at)
                VALUES (
                    'a0000000-0000-0000-0000-000000000001'::uuid,
                    'b0000000-0000-0000-0000-000000000001'::uuid,
                    'Test Workflow',
                    NOW(),
                    NOW()
                )
            """))
            session.commit()

        # Act: Upgrade to add column
        command.upgrade(alembic_config, "d4e5f6g7h8i0")

        with Session(test_engine) as session:
            # Verify workflow still exists and section_patterns is NULL
            result = session.execute(text("""
                SELECT name, section_patterns
                FROM workflows
                WHERE id = 'a0000000-0000-0000-0000-000000000001'::uuid
            """)).fetchone()
            assert result is not None
            assert result[0] == "Test Workflow"
            assert result[1] is None  # New column is NULL (backward compatible)

        # Act: Downgrade to remove column
        command.downgrade(alembic_config, "c3d4e5f6g7h9")

        with Session(test_engine) as session:
            # Verify workflow still exists after downgrade
            result = session.execute(text("""
                SELECT name
                FROM workflows
                WHERE id = 'a0000000-0000-0000-0000-000000000001'::uuid
            """)).fetchone()
            assert result is not None
            assert result[0] == "Test Workflow"

    def test_section_patterns_stores_json_array(self, alembic_config, test_engine):
        """Should store JSON array of regex patterns in section_patterns column."""
        # Arrange: Ensure migration is applied
        command.upgrade(alembic_config, "d4e5f6g7h8i0")

        with Session(test_engine) as session:
            # Insert workflow with custom patterns
            session.execute(text("""
                INSERT INTO workflows (id, organization_id, name, section_patterns, created_at, updated_at)
                VALUES (
                    'a0000000-0000-0000-0000-000000000002'::uuid,
                    'b0000000-0000-0000-0000-000000000002'::uuid,
                    'Medical Device Workflow',
                    '["^(\\\\d+(?:\\\\.\\\\d+)*\\\\.?\\\\s+[a-zA-Z][^\\\\n]{0,100})", "^([A-Z][A-Z\\\\s]{5,50})\\\\n"]'::json,
                    NOW(),
                    NOW()
                )
            """))
            session.commit()

        # Act: Read back the data
        with Session(test_engine) as session:
            result = session.execute(text("""
                SELECT section_patterns
                FROM workflows
                WHERE id = 'a0000000-0000-0000-0000-000000000002'::uuid
            """)).fetchone()

            # Assert: JSON array is correctly stored and retrieved
            assert result is not None
            patterns = result[0]
            assert isinstance(patterns, list)
            assert len(patterns) == 2
            assert all(isinstance(p, str) for p in patterns)
