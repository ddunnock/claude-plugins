"""Tests for RFC 6902 JSON diff and patch utilities."""

from scripts.json_diff import apply_patch, json_diff


class TestJsonDiff:
    """Tests for json_diff function."""

    def test_diff_add_new(self):
        """None -> dict produces a single add op for the full object."""
        result = json_diff(None, {"a": 1})
        assert result == [{"op": "add", "path": "", "value": {"a": 1}}]

    def test_diff_remove_key(self):
        """Removing a key produces a remove op."""
        result = json_diff({"a": 1, "b": 2}, {"a": 1})
        assert result == [{"op": "remove", "path": "/b"}]

    def test_diff_replace_value(self):
        """Changing a value produces a replace op."""
        result = json_diff({"a": 1}, {"a": 2})
        assert result == [{"op": "replace", "path": "/a", "value": 2}]

    def test_diff_nested_change(self):
        """Nested dict change produces correct path."""
        old = {"outer": {"inner": 1, "keep": True}}
        new = {"outer": {"inner": 2, "keep": True}}
        result = json_diff(old, new)
        assert result == [{"op": "replace", "path": "/outer/inner", "value": 2}]

    def test_diff_no_change(self):
        """Identical dicts produce an empty list."""
        d = {"a": 1, "b": {"c": 3}}
        result = json_diff(d, d)
        assert result == []

    def test_diff_add_key(self):
        """Adding a key produces an add op."""
        result = json_diff({"a": 1}, {"a": 1, "b": 2})
        assert result == [{"op": "add", "path": "/b", "value": 2}]

    def test_diff_multiple_ops(self):
        """Multiple changes produce sorted ops."""
        old = {"a": 1, "b": 2, "c": 3}
        new = {"a": 10, "c": 3, "d": 4}
        result = json_diff(old, new)
        assert len(result) == 3
        assert result[0] == {"op": "replace", "path": "/a", "value": 10}
        assert result[1] == {"op": "remove", "path": "/b"}
        assert result[2] == {"op": "add", "path": "/d", "value": 4}

    def test_diff_array_atomic_replace(self):
        """Array changes are treated as atomic replace, not element-level."""
        old = {"items": [1, 2, 3]}
        new = {"items": [1, 2, 3, 4]}
        result = json_diff(old, new)
        assert result == [{"op": "replace", "path": "/items", "value": [1, 2, 3, 4]}]

    def test_diff_deeply_nested(self):
        """Deeply nested changes produce correct multi-level paths."""
        old = {"a": {"b": {"c": 1}}}
        new = {"a": {"b": {"c": 2}}}
        result = json_diff(old, new)
        assert result == [{"op": "replace", "path": "/a/b/c", "value": 2}]


class TestApplyPatch:
    """Tests for apply_patch function."""

    def test_apply_patch_add(self):
        """Apply add operations."""
        base = {"a": 1}
        patch = [{"op": "add", "path": "/b", "value": 2}]
        result = apply_patch(base, patch)
        assert result == {"a": 1, "b": 2}
        # Original not mutated
        assert "b" not in base

    def test_apply_patch_remove(self):
        """Apply remove operations."""
        base = {"a": 1, "b": 2}
        patch = [{"op": "remove", "path": "/b"}]
        result = apply_patch(base, patch)
        assert result == {"a": 1}
        # Original not mutated
        assert "b" in base

    def test_apply_patch_replace(self):
        """Apply replace operations."""
        base = {"a": 1}
        patch = [{"op": "replace", "path": "/a", "value": 99}]
        result = apply_patch(base, patch)
        assert result == {"a": 99}

    def test_apply_patch_nested(self):
        """Apply operations at nested paths."""
        base = {"outer": {"inner": 1}}
        patch = [{"op": "replace", "path": "/outer/inner", "value": 2}]
        result = apply_patch(base, patch)
        assert result == {"outer": {"inner": 2}}

    def test_apply_patch_full_object_add(self):
        """Apply full-object add (path is empty)."""
        base = {}
        patch = [{"op": "add", "path": "", "value": {"x": 1}}]
        result = apply_patch(base, patch)
        assert result == {"x": 1}

    def test_roundtrip(self):
        """Diff then apply_patch recovers the new version."""
        old = {"name": "Widget", "version": 1, "status": "proposed"}
        new = {"name": "Widget v2", "version": 2, "status": "approved"}
        diff = json_diff(old, new)
        recovered = apply_patch(old, diff)
        assert recovered == new

    def test_roundtrip_from_none(self):
        """Diff from None then apply recovers the object."""
        new = {"a": 1, "b": {"c": 2}}
        diff = json_diff(None, new)
        recovered = apply_patch({}, diff)
        assert recovered == new
