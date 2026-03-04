/**
 * Reports API Service
 * Handle CSV/PDF export and summary reports
 */

const API_URL = "http://localhost:8000";

export const reportsAPI = {
  /**
   * Download transactions as CSV
   */
  async downloadTransactionsCSV(filters?: {
    startDate?: string;
    endDate?: string;
    category?: string;
    status?: string;
  }): Promise<Blob> {
    const token = localStorage.getItem("supabase.auth.token");
    if (!token) throw new Error("Not authenticated");

    const params = new URLSearchParams();
    if (filters?.startDate) params.append("start_date", filters.startDate);
    if (filters?.endDate) params.append("end_date", filters.endDate);
    if (filters?.category) params.append("category", filters.category);
    if (filters?.status) params.append("status", filters.status);

    const response = await fetch(
      `${API_URL}/api/reports/transactions/csv?${params.toString()}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to download CSV");
    }

    return response.blob();
  },

  /**
   * Get summary report with statistics
   */
  async getSummary(): Promise<any> {
    const token = localStorage.getItem("supabase.auth.token");
    if (!token) throw new Error("Not authenticated");

    const response = await fetch(`${API_URL}/api/reports/summary`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to get summary");
    }

    return response.json();
  },

  /**
   * Download predictions as CSV
   */
  async downloadPredictionsCSV(modelType?: string): Promise<Blob> {
    const token = localStorage.getItem("supabase.auth.token");
    if (!token) throw new Error("Not authenticated");

    const params = new URLSearchParams();
    if (modelType) params.append("model_type", modelType);

    const response = await fetch(
      `${API_URL}/api/reports/predictions/csv?${params.toString()}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to download predictions CSV");
    }

    return response.blob();
  },
};
