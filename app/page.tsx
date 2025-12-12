import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center text-gray-900">Bookstore Management System</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
          <Link
            href="/dashboard"
            className="group rounded-lg border border-gray-300 px-5 py-4 transition-colors hover:border-gray-400 hover:bg-gray-50 bg-white"
          >
            <h2 className="mb-3 text-2xl font-semibold text-gray-900">
              Dashboard{" "}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                -&gt;
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm text-gray-600">
              View statistics and overview
            </p>
          </Link>

          <Link
            href="/books"
            className="group rounded-lg border border-gray-300 px-5 py-4 transition-colors hover:border-gray-400 hover:bg-gray-50 bg-white"
          >
            <h2 className="mb-3 text-2xl font-semibold text-gray-900">
              Books{" "}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                -&gt;
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm text-gray-600">
              Browse and search our collection of books
            </p>
          </Link>

          <Link
            href="/orders"
            className="group rounded-lg border border-gray-300 px-5 py-4 transition-colors hover:border-gray-400 hover:bg-gray-50 bg-white"
          >
            <h2 className="mb-3 text-2xl font-semibold text-gray-900">
              Orders{" "}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                -&gt;
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm text-gray-600">
              View all customer orders
            </p>
          </Link>

          <Link
            href="/orders/create"
            className="group rounded-lg border border-gray-300 px-5 py-4 transition-colors hover:border-gray-400 hover:bg-gray-50 bg-white"
          >
            <h2 className="mb-3 text-2xl font-semibold text-gray-900">
              Create Order{" "}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                -&gt;
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm text-gray-600">
              Create a new customer order
            </p>
          </Link>

          <Link
            href="/rentals"
            className="group rounded-lg border border-gray-300 px-5 py-4 transition-colors hover:border-gray-400 hover:bg-gray-50 bg-white"
          >
            <h2 className="mb-3 text-2xl font-semibold text-gray-900">
              Rentals{" "}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                -&gt;
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm text-gray-600">
              Manage book rentals and returns
            </p>
          </Link>

          <Link
            href="/customers"
            className="group rounded-lg border border-gray-300 px-5 py-4 transition-colors hover:border-gray-400 hover:bg-gray-50 bg-white"
          >
            <h2 className="mb-3 text-2xl font-semibold text-gray-900">
              Customers{" "}
              <span className="inline-block transition-transform group-hover:translate-x-1">
                -&gt;
              </span>
            </h2>
            <p className="m-0 max-w-[30ch] text-sm text-gray-600">
              Manage customer information
            </p>
          </Link>
        </div>
      </div>
    </main>
  );
}
