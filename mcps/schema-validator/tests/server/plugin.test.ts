import { test, expect, describe } from "bun:test";

describe("plugin.json", () => {
  test("exists and is valid JSON", async () => {
    const file = Bun.file(
      import.meta.dir + "/../../.claude-plugin/plugin.json",
    );
    expect(await file.exists()).toBe(true);
    const content = await file.text();
    const plugin = JSON.parse(content);
    expect(plugin).toBeDefined();
  });

  test("has mcpServers.schema-validator with command bun", async () => {
    const file = Bun.file(
      import.meta.dir + "/../../.claude-plugin/plugin.json",
    );
    const plugin = JSON.parse(await file.text());
    expect(plugin.mcpServers).toBeDefined();
    expect(plugin.mcpServers["schema-validator"]).toBeDefined();
    expect(plugin.mcpServers["schema-validator"].command).toBe("bun");
  });

  test("args reference src/index.ts", async () => {
    const file = Bun.file(
      import.meta.dir + "/../../.claude-plugin/plugin.json",
    );
    const plugin = JSON.parse(await file.text());
    const args: string[] = plugin.mcpServers["schema-validator"].args;
    expect(args.some((arg: string) => arg.includes("src/index.ts"))).toBe(true);
  });
});
