"use client";
import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const X_ACCOUNT_TYPES = ['Blogger', 'Official', 'Ancore', 'WebSites', 'Others'] as const;
type XAccountType = typeof X_ACCOUNT_TYPES[number];

const parseApiError = (err: any): string => {
  const detail = err?.response?.data?.detail;
  if (!detail) return err?.message || 'Request failed';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map((e: any) => e.msg ?? JSON.stringify(e)).join('; ');
  return JSON.stringify(detail);
};

const toValidType = (t: string): XAccountType =>
  (X_ACCOUNT_TYPES as readonly string[]).includes(t) ? (t as XAccountType) : 'Blogger';

interface Account {
  id: string;
  x_account: string;
  x_account_id: string | null;
  x_account_type: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export default function XAccountManagement() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [xAccount, setXAccount] = useState('');
  const [xAccountType, setXAccountType] = useState<XAccountType>('Blogger');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Edit state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editType, setEditType] = useState<XAccountType>('Blogger');
  const [editActive, setEditActive] = useState(true);
  const [editLoading, setEditLoading] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const res = await axios.get(`${API_URL}/accounts`);
      setAccounts(res.data);
    } catch {
      setError('Failed to fetch accounts');
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await axios.post(`${API_URL}/accounts`, {
        x_account: xAccount,
        x_account_type: xAccountType,
      });
      setSuccess(`Account @${xAccount} added successfully!`);
      setXAccount('');
      setXAccountType('Blogger');
      fetchAccounts();
    } catch (err: any) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this account?')) return;
    setError('');
    setSuccess('');
    try {
      await axios.delete(`${API_URL}/accounts/${id}`);
      setSuccess('Account deleted.');
      fetchAccounts();
    } catch {
      setError('Failed to delete account');
    }
  };

  const startEdit = (acc: Account) => {
    setEditingId(acc.id);
    setEditType(toValidType(acc.x_account_type));
    setEditActive(acc.is_active);
  };

  const cancelEdit = () => {
    setEditingId(null);
  };

  const handleEdit = async (id: string) => {
    setEditLoading(true);
    setError('');
    setSuccess('');
    try {
      await axios.put(`${API_URL}/accounts/${id}`, {
        x_account_type: editType,
        is_active: editActive,
      });
      setSuccess('Account updated.');
      setEditingId(null);
      fetchAccounts();
    } catch (err: any) {
      setError(parseApiError(err));
    } finally {
      setEditLoading(false);
    }
  };

  return (
    <main className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/" className="text-gray-500 hover:text-gray-700 text-sm">← Back</Link>
        <h1 className="text-2xl font-bold">x_account-management</h1>
      </div>

      {/* Add Account Form */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Add X Account</h2>
        <form onSubmit={handleAdd} className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Twitter Account
            </label>
            <div className="flex">
              <span className="inline-flex items-center px-3 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 rounded-l-md text-sm">
                @
              </span>
              <input
                className="border border-gray-300 px-3 py-2 rounded-r-md w-48 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={xAccount}
                onChange={e => setXAccount(e.target.value)}
                placeholder="username"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              x_account_type
            </label>
            <select
              className="border border-gray-300 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={xAccountType}
              onChange={e => setXAccountType(e.target.value as XAccountType)}
            >
              {X_ACCOUNT_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            className="px-5 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
            disabled={loading}
          >
            {loading ? 'Adding...' : 'Add x Account'}
          </button>
        </form>

        {error && (
          <div className="mt-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
            {error}
          </div>
        )}
        {success && (
          <div className="mt-3 text-sm text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">
            {success}
          </div>
        )}
      </div>

      {/* Accounts Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Accounts ({accounts.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
              <tr>
                <th className="px-4 py-3 text-left">Account</th>
                <th className="px-4 py-3 text-left">Type</th>
                <th className="px-4 py-3 text-left">X Account ID</th>
                <th className="px-4 py-3 text-left">Created</th>
                <th className="px-4 py-3 text-left">Updated</th>
                <th className="px-4 py-3 text-center">Active</th>
                <th className="px-4 py-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {accounts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                    No accounts yet. Add one above.
                  </td>
                </tr>
              ) : (
                accounts.map(acc => (
                  <tr key={acc.id} className="hover:bg-gray-50">
                    {editingId === acc.id ? (
                      <>
                        {/* Editing row */}
                        <td className="px-4 py-3 font-medium text-gray-900">@{acc.x_account}</td>
                        <td className="px-4 py-3">
                          <select
                            className="border border-gray-300 px-2 py-1 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={editType}
                            onChange={e => setEditType(e.target.value as XAccountType)}
                          >
                            {X_ACCOUNT_TYPES.map(t => (
                              <option key={t} value={t}>{t}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-3 text-gray-500 font-mono text-xs">{acc.x_account_id || '—'}</td>
                        <td className="px-4 py-3 text-gray-500">{new Date(acc.created_at).toLocaleString()}</td>
                        <td className="px-4 py-3 text-gray-500">{new Date(acc.updated_at).toLocaleString()}</td>
                        <td className="px-4 py-3 text-center">
                          <input
                            type="checkbox"
                            checked={editActive}
                            onChange={e => setEditActive(e.target.checked)}
                            className="w-4 h-4 accent-blue-600"
                          />
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleEdit(acc.id)}
                              disabled={editLoading}
                              className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 disabled:opacity-50"
                            >
                              {editLoading ? 'Saving...' : 'Save'}
                            </button>
                            <button
                              onClick={cancelEdit}
                              className="px-3 py-1 bg-gray-200 text-gray-700 rounded text-xs hover:bg-gray-300"
                            >
                              Cancel
                            </button>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        {/* Normal row */}
                        <td className="px-4 py-3 font-medium text-gray-900">@{acc.x_account}</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium">
                            {acc.x_account_type}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-gray-500 font-mono text-xs">{acc.x_account_id || '—'}</td>
                        <td className="px-4 py-3 text-gray-500">{new Date(acc.created_at).toLocaleString()}</td>
                        <td className="px-4 py-3 text-gray-500">{new Date(acc.updated_at).toLocaleString()}</td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${acc.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                            {acc.is_active ? 'Yes' : 'No'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => startEdit(acc)}
                              className="px-3 py-1 bg-yellow-500 text-white rounded text-xs hover:bg-yellow-600"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDelete(acc.id)}
                              className="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
