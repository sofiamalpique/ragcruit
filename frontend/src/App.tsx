import { FormEvent, useMemo, useState } from "react";

import {
  CandidateCreatePayload,
  CandidateRead,
  CandidateSearchResult,
  createCandidate,
  searchCandidates,
} from "./api";


type CreateFormState = {
  full_name: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
  years_experience: string;
  skills: string;
};

type SearchFormState = {
  query_text: string;
  limit: string;
};

type StatusMessage = {
  kind: "success" | "error";
  text: string;
};

const initialCreateForm: CreateFormState = {
  full_name: "",
  email: "",
  phone: "",
  location: "",
  summary: "",
  years_experience: "",
  skills: "",
};

const initialSearchForm: SearchFormState = {
  query_text: "",
  limit: "5",
};


function toNullableText(value: string): string | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : trimmedValue;
}


function toCreatePayload(form: CreateFormState): CandidateCreatePayload {
  const yearsExperience = form.years_experience.trim();
  const skills = form.skills
    .split(",")
    .map((skill) => skill.trim())
    .filter(Boolean);

  return {
    full_name: form.full_name.trim(),
    email: form.email.trim(),
    phone: toNullableText(form.phone),
    location: toNullableText(form.location),
    summary: toNullableText(form.summary),
    years_experience: yearsExperience === "" ? null : Number(yearsExperience),
    skills,
  };
}


function App() {
  const [createForm, setCreateForm] = useState<CreateFormState>(initialCreateForm);
  const [createStatus, setCreateStatus] = useState<StatusMessage | null>(null);
  const [createdCandidate, setCreatedCandidate] = useState<CandidateRead | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const [searchForm, setSearchForm] = useState<SearchFormState>(initialSearchForm);
  const [searchResults, setSearchResults] = useState<CandidateSearchResult[]>([]);
  const [searchStatus, setSearchStatus] = useState<StatusMessage | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const resultCountText = useMemo(() => {
    if (!hasSearched) {
      return "Run a semantic search to see candidate matches.";
    }

    if (searchResults.length === 0) {
      return "No candidates matched the current query.";
    }

    return `${searchResults.length} candidate result${searchResults.length === 1 ? "" : "s"}`;
  }, [hasSearched, searchResults.length]);

  async function handleCreateSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setCreateStatus(null);

    try {
      const candidate = await createCandidate(toCreatePayload(createForm));
      setCreatedCandidate(candidate);
      setCreateStatus({
        kind: "success",
        text: `Candidate created successfully with id ${candidate.id}.`,
      });
    } catch (error) {
      setCreateStatus({
        kind: "error",
        text:
          error instanceof Error
            ? error.message
            : "Candidate creation failed.",
      });
    } finally {
      setIsCreating(false);
    }
  }

  async function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSearching(true);
    setHasSearched(true);
    setSearchStatus(null);

    try {
      const response = await searchCandidates({
        query_text: searchForm.query_text.trim(),
        limit: Number(searchForm.limit),
      });
      setSearchResults(response.results);
    } catch (error) {
      setSearchResults([]);
      setSearchStatus({
        kind: "error",
        text:
          error instanceof Error
            ? error.message
            : "Candidate search failed.",
      });
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">Ragcruit</p>
        <h1>AI hiring copilot frontend</h1>
        <p className="intro">
          Create candidate records, then query them through the current semantic
          search API from one small frontend surface.
        </p>
      </header>

      <div className="panel-grid">
        <section className="panel">
          <div className="panel-header">
            <h2>Create candidate</h2>
            <p>Submit a candidate to the existing backend create endpoint.</p>
          </div>

          <form className="form-grid" onSubmit={handleCreateSubmit}>
            <label className="field">
              <span>Full name</span>
              <input
                required
                value={createForm.full_name}
                onChange={(event) =>
                  setCreateForm((current) => ({
                    ...current,
                    full_name: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Email</span>
              <input
                required
                type="email"
                value={createForm.email}
                onChange={(event) =>
                  setCreateForm((current) => ({
                    ...current,
                    email: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Phone</span>
              <input
                value={createForm.phone}
                onChange={(event) =>
                  setCreateForm((current) => ({
                    ...current,
                    phone: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Location</span>
              <input
                value={createForm.location}
                onChange={(event) =>
                  setCreateForm((current) => ({
                    ...current,
                    location: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Summary</span>
              <textarea
                rows={4}
                value={createForm.summary}
                onChange={(event) =>
                  setCreateForm((current) => ({
                    ...current,
                    summary: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Years of experience</span>
              <input
                min="0"
                step="0.5"
                type="number"
                value={createForm.years_experience}
                onChange={(event) =>
                  setCreateForm((current) => ({
                    ...current,
                    years_experience: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Skills</span>
              <input
                placeholder="python, fastapi, postgresql"
                value={createForm.skills}
                onChange={(event) =>
                  setCreateForm((current) => ({
                    ...current,
                    skills: event.target.value,
                  }))
                }
              />
            </label>

            <div className="actions">
              <button className="button" disabled={isCreating} type="submit">
                {isCreating ? "Creating..." : "Create candidate"}
              </button>
            </div>
          </form>

          {createStatus ? (
            <div className={`status ${createStatus.kind}`}>{createStatus.text}</div>
          ) : null}

          {createdCandidate ? (
            <div className="summary-card">
              <strong>Latest created candidate</strong>
              <p>{createdCandidate.full_name}</p>
              <span className="muted">{createdCandidate.email}</span>
            </div>
          ) : null}
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Search candidates</h2>
            <p>Run semantic search through the current pgvector-backed API.</p>
          </div>

          <form className="form-grid" onSubmit={handleSearchSubmit}>
            <label className="field">
              <span>Query text</span>
              <textarea
                required
                rows={4}
                placeholder="Find backend engineers with strong Python and PostgreSQL experience"
                value={searchForm.query_text}
                onChange={(event) =>
                  setSearchForm((current) => ({
                    ...current,
                    query_text: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Limit</span>
              <input
                min="1"
                step="1"
                type="number"
                value={searchForm.limit}
                onChange={(event) =>
                  setSearchForm((current) => ({
                    ...current,
                    limit: event.target.value,
                  }))
                }
              />
            </label>

            <div className="actions">
              <button className="button" disabled={isSearching} type="submit">
                {isSearching ? "Searching..." : "Search candidates"}
              </button>
            </div>
          </form>

          {searchStatus ? (
            <div className={`status ${searchStatus.kind}`}>{searchStatus.text}</div>
          ) : null}
        </section>
      </div>

      <section className="panel results-panel">
        <div className="panel-header">
          <h2>Search results</h2>
          <p>{resultCountText}</p>
        </div>

        <div className="results-list">
          {searchResults.map((result) => (
            <article className="result-card" key={result.candidate.id}>
              <div className="result-meta">
                <div>
                  <h3>{result.candidate.full_name}</h3>
                  <p className="muted">{result.candidate.email}</p>
                </div>
                <span className="score-pill">
                  Similarity {result.similarity_score.toFixed(3)}
                </span>
              </div>

              <dl className="details-grid">
                <div>
                  <dt>Location</dt>
                  <dd>{result.candidate.location ?? "Not provided"}</dd>
                </div>
                <div>
                  <dt>Phone</dt>
                  <dd>{result.candidate.phone ?? "Not provided"}</dd>
                </div>
                <div>
                  <dt>Experience</dt>
                  <dd>
                    {result.candidate.years_experience ?? "Not provided"}
                  </dd>
                </div>
              </dl>

              <p className="summary-text">
                {result.candidate.summary ?? "No summary provided."}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}


export default App;
