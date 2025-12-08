'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Customer {
  customer_id: number;
  first_name: string;
  last_name: string;
  customer_type: string;
  phone_number: string;
  zip_code: number;
}

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    customer_type: 'Regular',
    phone_number: '',
    zip_code: 10001,
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await fetch('/api/py/customers');
      const data = await response.json();
      setCustomers(data);
    } catch (error) {
      console.error('Error fetching customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/py/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        fetchCustomers();
        setShowForm(false);
        setFormData({
          first_name: '',
          last_name: '',
          customer_type: 'Regular',
          phone_number: '',
          zip_code: 10001,
        });
      }
    } catch (error) {
      console.error('Error creating customer:', error);
    }
  };

  if (loading) {
    return <div className="p-8 bg-white min-h-screen text-gray-900">Loading...</div>;
  }

  return (
    <div className="container mx-auto p-8 bg-white min-h-screen">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          ← Back to Home
        </Link>
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {showForm ? 'Cancel' : 'Add Customer'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-6 border border-gray-300 rounded-lg bg-gray-50">
          <div className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="First Name"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded bg-white text-gray-900 placeholder-gray-500"
              required
            />
            <input
              type="text"
              placeholder="Last Name"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded bg-white text-gray-900 placeholder-gray-500"
              required
            />
            <select
              value={formData.customer_type}
              onChange={(e) => setFormData({ ...formData, customer_type: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded bg-white text-gray-900"
            >
              <option value="Regular">Regular</option>
              <option value="Premium">Premium</option>
            </select>
            <input
              type="text"
              placeholder="Phone (123-456-7890)"
              value={formData.phone_number}
              onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded bg-white text-gray-900 placeholder-gray-500"
              required
            />
            <input
              type="number"
              placeholder="Zip Code"
              value={formData.zip_code}
              onChange={(e) => setFormData({ ...formData, zip_code: parseInt(e.target.value) })}
              className="px-4 py-2 border border-gray-300 rounded bg-white text-gray-900 placeholder-gray-500"
              required
            />
          </div>
          <button
            type="submit"
            className="mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Create Customer
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {customers.map((customer) => (
          <div key={customer.customer_id} className="border border-gray-300 rounded-lg p-6 shadow-md bg-white">
            <h2 className="text-xl font-semibold mb-2 text-gray-900">
              {customer.first_name} {customer.last_name}
            </h2>
            <p className="text-gray-600">Type: {customer.customer_type}</p>
            <p className="text-gray-600">Phone: {customer.phone_number}</p>
            <p className="text-gray-600">Zip: {customer.zip_code}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

