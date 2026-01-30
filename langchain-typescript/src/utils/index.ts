import path from "path";

const WORKDIR = process.cwd();
export function safePath(p: string): string {
  const resolved = path.resolve(WORKDIR, p);
  if (!resolved.startsWith(WORKDIR)) throw new Error(`路径逃逸工作区: ${p}`);
  return resolved;
}
