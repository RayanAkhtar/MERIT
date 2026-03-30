import CVUpload from "../../components/CVUpload";

export default function ExtractCVsPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950 px-4 py-12 md:py-16">
      <div className="max-w-4xl mx-auto space-y-4">
        <h1 className="text-3xl font-bold dark:text-white">Extract CVs</h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Upload candidate CVs to extract relevant skills and information.
        </p>
        <CVUpload />
      </div>
    </main>
  );
}
