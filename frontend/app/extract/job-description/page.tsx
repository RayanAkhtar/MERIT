import JobDescriptionUpload from "../../components/JobDescriptionUpload";

export default function ExtractJobDescriptionPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950 px-4 py-12 md:py-16">
      <div className="max-w-4xl mx-auto space-y-4">
        <h1 className="text-3xl font-bold dark:text-white">Extract Job Description</h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Upload Job Description files to extract refined metadata and benchmarks.
        </p>
        <JobDescriptionUpload />
      </div>
    </main>
  );
}
