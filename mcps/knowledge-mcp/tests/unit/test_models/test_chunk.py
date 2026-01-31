"""Unit tests for KnowledgeChunk model and RCCA metadata extraction."""

from __future__ import annotations

import pytest

from knowledge_mcp.models.chunk import KnowledgeChunk
from knowledge_mcp.ingest.pipeline import IngestionPipeline


class TestKnowledgeChunkRCCAFields:
    """Tests for KnowledgeChunk RCCA metadata fields."""

    def test_rcca_fields_have_none_defaults(self) -> None:
        """Test that RCCA fields default to None."""
        chunk = KnowledgeChunk(
            id="test-id",
            document_id="test-doc",
            document_title="Test Document",
            document_type="standard",
            content="Test content",
            content_hash="abc123",
            token_count=10,
        )

        assert chunk.standard is None
        assert chunk.domain is None
        assert chunk.version is None
        assert chunk.standard_family is None
        assert chunk.supersedes is None
        assert chunk.related_standards == []

    def test_rcca_fields_accept_valid_values(self) -> None:
        """Test that RCCA fields accept valid values."""
        chunk = KnowledgeChunk(
            id="test-id",
            document_id="aiag-vda-fmea-2019",
            document_title="AIAG-VDA FMEA Handbook",
            document_type="standard",
            content="Failure mode analysis content",
            content_hash="def456",
            token_count=25,
            standard="AIAG-VDA FMEA 2019",
            domain="fmea",
            version="2019",
            standard_family="fmea_methodology",
            supersedes="AIAG FMEA-4 2008",
            related_standards=["ISO 26262", "IEC 61508"],
        )

        assert chunk.standard == "AIAG-VDA FMEA 2019"
        assert chunk.domain == "fmea"
        assert chunk.version == "2019"
        assert chunk.standard_family == "fmea_methodology"
        assert chunk.supersedes == "AIAG FMEA-4 2008"
        assert chunk.related_standards == ["ISO 26262", "IEC 61508"]

    def test_to_dict_includes_rcca_fields(self) -> None:
        """Test that to_dict() includes all RCCA fields."""
        chunk = KnowledgeChunk(
            id="test-id",
            document_id="mil-std-882e",
            document_title="MIL-STD-882E",
            document_type="standard",
            content="System safety requirements",
            content_hash="ghi789",
            token_count=15,
            standard="MIL-STD-882E",
            domain="safety",
            version="E",
            standard_family="safety",
        )

        result = chunk.to_dict()

        assert "standard" in result
        assert "domain" in result
        assert "version" in result
        assert "standard_family" in result
        assert "supersedes" in result
        assert "related_standards" in result

        assert result["standard"] == "MIL-STD-882E"
        assert result["domain"] == "safety"
        assert result["version"] == "E"
        assert result["standard_family"] == "safety"
        assert result["supersedes"] is None
        assert result["related_standards"] == []

    def test_to_dict_with_none_rcca_fields(self) -> None:
        """Test that to_dict() correctly serializes None RCCA fields."""
        chunk = KnowledgeChunk(
            id="test-id",
            document_id="unknown-doc",
            document_title="Unknown Document",
            document_type="guide",
            content="Some content",
            content_hash="jkl012",
            token_count=5,
        )

        result = chunk.to_dict()

        assert result["standard"] is None
        assert result["domain"] is None
        assert result["version"] is None
        assert result["standard_family"] is None
        assert result["supersedes"] is None
        assert result["related_standards"] == []


class TestExtractStandardName:
    """Tests for IngestionPipeline._extract_standard_name method."""

    @pytest.fixture
    def pipeline(self) -> IngestionPipeline:
        """Create an IngestionPipeline instance."""
        return IngestionPipeline()

    def test_aiag_vda_fmea_pattern(self, pipeline: IngestionPipeline) -> None:
        """Test AIAG-VDA FMEA pattern extraction."""
        assert pipeline._extract_standard_name("aiag-vda-fmea-2019") == "AIAG-VDA FMEA 2019"
        assert pipeline._extract_standard_name("aiag_vda_fmea_2019") == "AIAG-VDA FMEA 2019"
        assert pipeline._extract_standard_name("aiagvdafmea2019") == "AIAG-VDA FMEA 2019"

    def test_mil_std_882_pattern(self, pipeline: IngestionPipeline) -> None:
        """Test MIL-STD-882 pattern extraction."""
        assert pipeline._extract_standard_name("mil-std-882e") == "MIL-STD-882E"
        assert pipeline._extract_standard_name("mil_std_882e") == "MIL-STD-882E"
        assert pipeline._extract_standard_name("milstd882e") == "MIL-STD-882E"
        assert pipeline._extract_standard_name("mil-std-882") == "MIL-STD-882"

    def test_iso_pattern(self, pipeline: IngestionPipeline) -> None:
        """Test ISO standard pattern extraction."""
        assert pipeline._extract_standard_name("iso-9001-2015") == "ISO 9001:2015"
        assert pipeline._extract_standard_name("iso_9001_2015") == "ISO 9001:2015"
        assert pipeline._extract_standard_name("iso-26262-2018") == "ISO 26262:2018"

    def test_iec_pattern(self, pipeline: IngestionPipeline) -> None:
        """Test IEC standard pattern extraction."""
        assert pipeline._extract_standard_name("iec-61508-2010") == "IEC 61508:2010"
        assert pipeline._extract_standard_name("iec_61508_2010") == "IEC 61508:2010"

    def test_sae_pattern(self, pipeline: IngestionPipeline) -> None:
        """Test SAE standard pattern extraction."""
        assert pipeline._extract_standard_name("sae-j1739") == "SAE J1739"
        assert pipeline._extract_standard_name("sae_j1739") == "SAE J1739"

    def test_unknown_pattern_returns_none(self, pipeline: IngestionPipeline) -> None:
        """Test that unknown patterns return None."""
        assert pipeline._extract_standard_name("unknown-doc") is None
        assert pipeline._extract_standard_name("random-standard") is None
        assert pipeline._extract_standard_name("ieee-15288") is None  # Not in patterns


class TestExtractDomain:
    """Tests for IngestionPipeline._extract_domain method."""

    @pytest.fixture
    def pipeline(self) -> IngestionPipeline:
        """Create an IngestionPipeline instance."""
        return IngestionPipeline()

    def test_fmea_domain(self, pipeline: IngestionPipeline) -> None:
        """Test FMEA domain extraction."""
        assert pipeline._extract_domain("aiag-vda-fmea-2019") == "fmea"
        assert pipeline._extract_domain("vda-fmea-guide") == "fmea"
        assert pipeline._extract_domain("sae-j1739-fmea") == "fmea"
        assert pipeline._extract_domain("some-fmea-document") == "fmea"

    def test_safety_domain(self, pipeline: IngestionPipeline) -> None:
        """Test safety domain extraction."""
        assert pipeline._extract_domain("mil-std-882e") == "safety"
        assert pipeline._extract_domain("iec-61508-2010") == "safety"
        assert pipeline._extract_domain("iso-26262-2018") == "safety"

    def test_quality_domain(self, pipeline: IngestionPipeline) -> None:
        """Test quality domain extraction."""
        assert pipeline._extract_domain("iso-9001-2015") == "quality"
        assert pipeline._extract_domain("iatf-16949-2016") == "quality"
        assert pipeline._extract_domain("as-9100-rev-d") == "quality"

    def test_unknown_domain_returns_none(self, pipeline: IngestionPipeline) -> None:
        """Test that unknown domains return None."""
        assert pipeline._extract_domain("unknown-doc") is None
        assert pipeline._extract_domain("ieee-15288") is None


class TestExtractVersion:
    """Tests for IngestionPipeline._extract_version method."""

    @pytest.fixture
    def pipeline(self) -> IngestionPipeline:
        """Create an IngestionPipeline instance."""
        return IngestionPipeline()

    def test_year_version(self, pipeline: IngestionPipeline) -> None:
        """Test year version extraction."""
        assert pipeline._extract_version("aiag-vda-fmea-2019") == "2019"
        assert pipeline._extract_version("iso-9001-2015") == "2015"
        assert pipeline._extract_version("iec-61508-2010") == "2010"

    def test_letter_version(self, pipeline: IngestionPipeline) -> None:
        """Test letter version extraction."""
        assert pipeline._extract_version("mil-std-882e") == "E"
        assert pipeline._extract_version("standard-123a") == "A"

    def test_no_version_returns_none(self, pipeline: IngestionPipeline) -> None:
        """Test that documents without version return None."""
        assert pipeline._extract_version("unknown-doc") is None
        assert pipeline._extract_version("some-standard") is None


class TestClassifyFamily:
    """Tests for IngestionPipeline._classify_family method."""

    @pytest.fixture
    def pipeline(self) -> IngestionPipeline:
        """Create an IngestionPipeline instance."""
        return IngestionPipeline()

    def test_fmea_family(self, pipeline: IngestionPipeline) -> None:
        """Test FMEA domain maps to fmea_methodology family."""
        assert pipeline._classify_family("fmea") == "fmea_methodology"

    def test_safety_family(self, pipeline: IngestionPipeline) -> None:
        """Test safety domain maps to safety family."""
        assert pipeline._classify_family("safety") == "safety"

    def test_quality_family(self, pipeline: IngestionPipeline) -> None:
        """Test quality domain maps to quality family."""
        assert pipeline._classify_family("quality") == "quality"

    def test_reliability_family(self, pipeline: IngestionPipeline) -> None:
        """Test reliability domain maps to reliability family."""
        assert pipeline._classify_family("reliability") == "reliability"

    def test_none_returns_none(self, pipeline: IngestionPipeline) -> None:
        """Test that None domain returns None family."""
        assert pipeline._classify_family(None) is None

    def test_unknown_domain_returns_none(self, pipeline: IngestionPipeline) -> None:
        """Test that unknown domain returns None family."""
        assert pipeline._classify_family("unknown") is None


class TestRCCAMetadataIntegration:
    """Integration tests for RCCA metadata in ingestion pipeline."""

    @pytest.fixture
    def pipeline(self) -> IngestionPipeline:
        """Create an IngestionPipeline instance."""
        return IngestionPipeline()

    def test_full_extraction_aiag_vda(self, pipeline: IngestionPipeline) -> None:
        """Test full RCCA metadata extraction for AIAG-VDA document."""
        doc_id = "aiag-vda-fmea-2019"

        standard = pipeline._extract_standard_name(doc_id)
        domain = pipeline._extract_domain(doc_id)
        version = pipeline._extract_version(doc_id)
        family = pipeline._classify_family(domain)

        assert standard == "AIAG-VDA FMEA 2019"
        assert domain == "fmea"
        assert version == "2019"
        assert family == "fmea_methodology"

    def test_full_extraction_mil_std(self, pipeline: IngestionPipeline) -> None:
        """Test full RCCA metadata extraction for MIL-STD document."""
        doc_id = "mil-std-882e"

        standard = pipeline._extract_standard_name(doc_id)
        domain = pipeline._extract_domain(doc_id)
        version = pipeline._extract_version(doc_id)
        family = pipeline._classify_family(domain)

        assert standard == "MIL-STD-882E"
        assert domain == "safety"
        assert version == "E"
        assert family == "safety"

    def test_full_extraction_iso_quality(self, pipeline: IngestionPipeline) -> None:
        """Test full RCCA metadata extraction for ISO quality document."""
        doc_id = "iso-9001-2015"

        standard = pipeline._extract_standard_name(doc_id)
        domain = pipeline._extract_domain(doc_id)
        version = pipeline._extract_version(doc_id)
        family = pipeline._classify_family(domain)

        assert standard == "ISO 9001:2015"
        assert domain == "quality"
        assert version == "2015"
        assert family == "quality"
