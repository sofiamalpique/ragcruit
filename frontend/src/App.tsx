import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  CandidateCreatePayload,
  CandidateRead,
  CandidateSearchResult,
  JobCreatePayload,
  JobMatchResult,
  JobRead,
  createJob,
  createCandidate,
  listJobs,
  matchJob,
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

type JobCreateFormState = {
  title: string;
  company_name: string;
  location: string;
  description: string;
  requirements: string;
  min_years_experience: string;
};

type JobMatchFormState = {
  job_posting_id: string;
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

const initialJobCreateForm: JobCreateFormState = {
  title: "",
  company_name: "",
  location: "",
  description: "",
  requirements: "",
  min_years_experience: "",
};

const initialJobMatchForm: JobMatchFormState = {
  job_posting_id: "",
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

function toJobCreatePayload(form: JobCreateFormState): JobCreatePayload {
  const minYearsExperience = form.min_years_experience.trim();

  return {
    title: form.title.trim(),
    company_name: toNullableText(form.company_name),
    location: toNullableText(form.location),
    description: form.description.trim(),
    requirements: toNullableText(form.requirements),
    min_years_experience:
      minYearsExperience === "" ? null : Number(minYearsExperience),
  };
}

type CandidateResultCardProps = {
  result: CandidateSearchResult | JobMatchResult;
};

function CandidateResultCard({ result }: CandidateResultCardProps) {
  const isJobMatchResult = "relevance_score" in result;

  return (
    <article className="result-card">
      <div className="result-meta">
        <div>
          <h3>{result.candidate.full_name}</h3>
          <p className="muted">{result.candidate.email}</p>
        </div>
        <div className="score-stack">
          {isJobMatchResult ? (
            <span className="score-pill score-pill-primary">
              Relevance {result.relevance_score.toFixed(3)}
            </span>
          ) : null}
          <span className="score-pill">
            Similarity {result.similarity_score.toFixed(3)}
          </span>
        </div>
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
          <dd>{result.candidate.years_experience ?? "Not provided"}</dd>
        </div>
      </dl>

      <p className="summary-text">
        {result.candidate.summary ?? "No summary provided."}
      </p>

      {isJobMatchResult && result.match_reasons.length > 0 ? (
        <ul className="reason-list">
          {result.match_reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
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

  const [jobCreateForm, setJobCreateForm] = useState<JobCreateFormState>(
    initialJobCreateForm,
  );
  const [jobCreateStatus, setJobCreateStatus] = useState<StatusMessage | null>(
    null,
  );
  const [createdJob, setCreatedJob] = useState<JobRead | null>(null);
  const [isCreatingJob, setIsCreatingJob] = useState(false);
  const [jobs, setJobs] = useState<JobRead[]>([]);
  const [jobsStatus, setJobsStatus] = useState<StatusMessage | null>(null);
  const [isLoadingJobs, setIsLoadingJobs] = useState(false);

  const [jobMatchForm, setJobMatchForm] = useState<JobMatchFormState>(
    initialJobMatchForm,
  );
  const [jobMatchResults, setJobMatchResults] = useState<JobMatchResult[]>([]);
  const [jobMatchStatus, setJobMatchStatus] = useState<StatusMessage | null>(
    null,
  );
  const [hasMatchedJob, setHasMatchedJob] = useState(false);
  const [isMatchingJob, setIsMatchingJob] = useState(false);

  const candidateSearchCountText = useMemo(() => {
    if (!hasSearched) {
      return "Run a semantic search to see candidate matches.";
    }

    if (searchResults.length === 0) {
      return "No candidates matched the current query.";
    }

    return `${searchResults.length} candidate result${searchResults.length === 1 ? "" : "s"}`;
  }, [hasSearched, searchResults.length]);

  const jobMatchCountText = useMemo(() => {
    if (!hasMatchedJob) {
      return "Select a job posting and run matching to see candidate results.";
    }

    if (jobMatchResults.length === 0) {
      return "No candidates matched the selected job posting.";
    }

    return `${jobMatchResults.length} matched candidate${jobMatchResults.length === 1 ? "" : "s"}`;
  }, [hasMatchedJob, jobMatchResults.length]);

  useEffect(() => {
    async function loadInitialJobs() {
      setIsLoadingJobs(true);
      setJobsStatus(null);

      try {
        const jobPostings = await listJobs();
        setJobs(jobPostings);
        setJobMatchForm((current) => ({
          ...current,
          job_posting_id:
            current.job_posting_id !== ""
              ? current.job_posting_id
              : (jobPostings[0]?.id?.toString() ?? ""),
        }));
      } catch (error) {
        setJobsStatus({
          kind: "error",
          text: error instanceof Error ? error.message : "Loading jobs failed.",
        });
      } finally {
        setIsLoadingJobs(false);
      }
    }

    void loadInitialJobs();
  }, []);

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

  async function handleJobCreateSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreatingJob(true);
    setJobCreateStatus(null);

    try {
      const jobPosting = await createJob(toJobCreatePayload(jobCreateForm));
      setCreatedJob(jobPosting);
      setJobs((current) => [
        jobPosting,
        ...current.filter((existingJob) => existingJob.id !== jobPosting.id),
      ]);
      setJobMatchForm((current) => ({
        ...current,
        job_posting_id: jobPosting.id.toString(),
      }));
      setJobCreateStatus({
        kind: "success",
        text: `Job posting created successfully with id ${jobPosting.id}.`,
      });
      setJobCreateForm(initialJobCreateForm);
    } catch (error) {
      setJobCreateStatus({
        kind: "error",
        text:
          error instanceof Error ? error.message : "Job posting creation failed.",
      });
    } finally {
      setIsCreatingJob(false);
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

  async function handleJobMatchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (jobMatchForm.job_posting_id === "") {
      setJobMatchStatus({
        kind: "error",
        text: "Select a job posting before running matching.",
      });
      return;
    }

    setIsMatchingJob(true);
    setHasMatchedJob(true);
    setJobMatchStatus(null);

    try {
      const response = await matchJob(Number(jobMatchForm.job_posting_id), {
        limit: Number(jobMatchForm.limit),
      });
      setJobMatchResults(response.results);
    } catch (error) {
      setJobMatchResults([]);
      setJobMatchStatus({
        kind: "error",
        text: error instanceof Error ? error.message : "Job matching failed.",
      });
    } finally {
      setIsMatchingJob(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">Ragcruit</p>
        <h1>AI hiring copilot frontend</h1>
        <p className="intro">
          Create candidates and job postings, then run semantic search and
          job-based matching from one small frontend surface.
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

        <section className="panel">
          <div className="panel-header">
            <h2>Create job posting</h2>
            <p>Create a job and persist its embedding for future matching.</p>
          </div>

          <form className="form-grid" onSubmit={handleJobCreateSubmit}>
            <label className="field">
              <span>Title</span>
              <input
                required
                value={jobCreateForm.title}
                onChange={(event) =>
                  setJobCreateForm((current) => ({
                    ...current,
                    title: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Company</span>
              <input
                value={jobCreateForm.company_name}
                onChange={(event) =>
                  setJobCreateForm((current) => ({
                    ...current,
                    company_name: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Location</span>
              <input
                value={jobCreateForm.location}
                onChange={(event) =>
                  setJobCreateForm((current) => ({
                    ...current,
                    location: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Description</span>
              <textarea
                required
                rows={4}
                value={jobCreateForm.description}
                onChange={(event) =>
                  setJobCreateForm((current) => ({
                    ...current,
                    description: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Requirements</span>
              <textarea
                rows={4}
                value={jobCreateForm.requirements}
                onChange={(event) =>
                  setJobCreateForm((current) => ({
                    ...current,
                    requirements: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Minimum years of experience</span>
              <input
                min="0"
                step="0.5"
                type="number"
                value={jobCreateForm.min_years_experience}
                onChange={(event) =>
                  setJobCreateForm((current) => ({
                    ...current,
                    min_years_experience: event.target.value,
                  }))
                }
              />
            </label>

            <div className="actions">
              <button className="button" disabled={isCreatingJob} type="submit">
                {isCreatingJob ? "Creating..." : "Create job posting"}
              </button>
            </div>
          </form>

          {jobCreateStatus ? (
            <div className={`status ${jobCreateStatus.kind}`}>
              {jobCreateStatus.text}
            </div>
          ) : null}

          {createdJob ? (
            <div className="summary-card">
              <strong>Latest created job</strong>
              <p>{createdJob.title}</p>
              <span className="muted">
                {createdJob.company_name ?? "No company provided"}
              </span>
            </div>
          ) : null}
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Match candidates to a job</h2>
            <p>
              Use the stored job embedding to retrieve semantically similar
              candidates.
            </p>
          </div>

          <form className="form-grid" onSubmit={handleJobMatchSubmit}>
            <label className="field">
              <span>Job posting</span>
              <select
                value={jobMatchForm.job_posting_id}
                onChange={(event) =>
                  setJobMatchForm((current) => ({
                    ...current,
                    job_posting_id: event.target.value,
                  }))
                }
              >
                <option value="">Select a job posting</option>
                {jobs.map((jobPosting) => (
                  <option key={jobPosting.id} value={jobPosting.id}>
                    {jobPosting.title}
                    {jobPosting.company_name ? ` · ${jobPosting.company_name}` : ""}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Limit</span>
              <input
                min="1"
                step="1"
                type="number"
                value={jobMatchForm.limit}
                onChange={(event) =>
                  setJobMatchForm((current) => ({
                    ...current,
                    limit: event.target.value,
                  }))
                }
              />
            </label>

            <div className="actions">
              <button
                className="button"
                disabled={isMatchingJob || isLoadingJobs}
                type="submit"
              >
                {isMatchingJob ? "Matching..." : "Match candidates"}
              </button>
            </div>
          </form>

          {jobsStatus ? (
            <div className={`status ${jobsStatus.kind}`}>{jobsStatus.text}</div>
          ) : null}

          {jobMatchStatus ? (
            <div className={`status ${jobMatchStatus.kind}`}>
              {jobMatchStatus.text}
            </div>
          ) : null}

          <div className="summary-card">
            <strong>Available jobs</strong>
            <p>{jobs.length} loaded from the backend</p>
            <span className="muted">
              {isLoadingJobs
                ? "Loading jobs..."
                : "Create a job first if this list is empty."}
            </span>
          </div>
        </section>
      </div>

      <div className="panel-grid">
        <section className="panel results-panel">
          <div className="panel-header">
            <h2>Candidate search results</h2>
            <p>{candidateSearchCountText}</p>
          </div>

          <div className="results-list">
            {searchResults.map((result) => (
              <CandidateResultCard
                key={`candidate-search-${result.candidate.id}`}
                result={result}
              />
            ))}
          </div>
        </section>

        <section className="panel results-panel">
          <div className="panel-header">
            <h2>Job match results</h2>
            <p>{jobMatchCountText}</p>
          </div>

          <div className="results-list">
            {jobMatchResults.map((result) => (
              <CandidateResultCard
                key={`job-match-${result.candidate.id}`}
                result={result}
              />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}


export default App;
