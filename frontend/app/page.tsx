'use client'

import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-8">
      <h1 className="text-4xl font-bold mb-4">eNewPaper</h1>
      <p className="mb-8 text-lg text-gray-700">Twitter/X Account Management System</p>
      <div className="flex gap-4">
        <Link href="/x-account-management">
          <button className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
            x_account-management
          </button>
        </Link>
      </div>
    </main>
  );
}
