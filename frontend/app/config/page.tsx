import Image from 'next/image';
import FileUpload from "../components/FileUpload";

export default function ConfigPage() {
  return (
    <main className="min-h-screen bg-white dark:bg-zinc-950">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div className="mb-8">
          <div className="flex justify-center mb-6">
            <Image
              src="/MERIT-white-transparent.png"
              alt="MERIT Logo"
              width={200}
              height={67}
              className="h-32 w-auto dark:hidden"
              priority
            />
            <Image
              src="/MERIT-black-transparent.png"
              alt="MERIT Logo"
              width={200}
              height={67}
              className="h-32 w-auto hidden dark:block"
              priority
            />
          </div>
          <p className="text-zinc-600 dark:text-zinc-400">
            Batch upload candidate CVs to see what datasources are available.
          </p>
        </div>
        <FileUpload />
      </div>
    </main>
  );
}

