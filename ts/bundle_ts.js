import { svelte } from "@sveltejs/vite-plugin-svelte";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "vite";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const srcDir = path.resolve(__dirname, "src");

const packageJson = JSON.parse(readFileSync(path.resolve(__dirname, "package.json"), "utf8"));
const addonName = packageJson.name.split("_").map(part => part[0].toUpperCase() + part.slice(1).toLowerCase()).join("");

const moduleName = process.argv[2];
if (!moduleName) {
    console.error("Usage: node bundle_ts.js <module_name>");
    process.exit(1);
}

await build({
    configFile: false,
    plugins: [svelte()],
    build: {
        outDir: "../src/web/build/",
        emptyOutDir: false,
        lib: {
            entry: path.join(srcDir, moduleName, "index.ts"),
            name: addonName,
            fileName: () => `${moduleName}.js`,
            cssFileName: moduleName,
            formats: ["umd"],
        },
        minify: true,
        sourcemap: false,
        target: "es2020",
    },
});
