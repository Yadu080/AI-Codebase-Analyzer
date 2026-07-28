const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export type RepoSummary = {
  languages: string[];
  main_modules: string[];
  total_files: number;
  total_chunks: number;
};

export type AnalyzeResponse = {
  message: string;
  chunks: number;
  summary: RepoSummary;
};

export type AskResponse = {
  answer: string;
};

export type ArchitectureResponse = {
  architecture: Record<string, string[]>;
};

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data?.detail === "string") detail = data.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  return res.json() as Promise<T>;
}

export function getApiUrl() {
  return API_URL;
}

export function analyzeRepo(repoUrl: string) {
  return postJson<AnalyzeResponse>("/analyze", { repo_url: repoUrl });
}

export function askQuestion(question: string) {
  return postJson<AskResponse>("/ask", { question });
}

export function fetchArchitecture(repoUrl: string) {
  return postJson<ArchitectureResponse>("/architecture", {
    repo_url: repoUrl,
  });
}
