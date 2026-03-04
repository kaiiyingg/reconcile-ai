// Transaction API Service
const API_BASE = 'http://localhost:8000/api/transactions';

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const token = localStorage.getItem('access_token');
  
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'x-user-id': user.id || ''
  };
}

export const transactionAPI = {
  // Upload CSV
  async uploadCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: formData
    });
    
    if (!response.ok) throw new Error('Upload failed');
    return response.json();
  },

  // Generate demo data
  async generateDemo(count: number = 100) {
    const response = await fetch(`${API_BASE}/generate-demo?count=${count}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Failed to generate demo');
    return response.json();
  },

  // Download demo CSV
  async downloadDemoCSV(count: number = 100) {
    const response = await fetch(`${API_BASE}/download-demo-csv?count=${count}`);
    const blob = await response.blob();
    
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'demo_transactions.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  },

  // Get transactions
  async getTransactions(params?: {
    start_date?: string;
    end_date?: string;
    category?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) {
    const query = new URLSearchParams(params as any).toString();
    const response = await fetch(`${API_BASE}?${query}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    // Backend returns {total, transactions}, we just need the transactions array
    return data.transactions || [];
  },

  // Get summary
  async getSummary(days: number = 30) {
    const response = await fetch(`${API_BASE}/summary?days=${days}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Failed to fetch summary');
    return response.json();
  },

  // Get single transaction
  async getTransaction(id: string) {
    const response = await fetch(`${API_BASE}/${id}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Transaction not found');
    return response.json();
  },

  // Update status
  async updateStatus(id: string, status: string) {
    const response = await fetch(`${API_BASE}/${id}/status?status=${status}`, {
      method: 'PATCH',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Failed to update status');
    return response.json();
  },

  // Bulk delete by source
  async bulkDelete(source: string) {
    const response = await fetch(`${API_BASE}/bulk-delete?source=${source}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) throw new Error('Failed to delete');
    return response.json();
  }
};
