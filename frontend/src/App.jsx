import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:5000/api/pois";

function App() {
  const [pois, setPois] = useState([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [visits, setVisits] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editCity, setEditCity] = useState("");
  const [editVisits, setEditVisits] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [stats, setStats] = useState(null);

  // ===== Fetch POIs =====
  const fetchPois = (resetPage = true) => {
    fetch(API_BASE)
      .then((res) => res.json())
      .then((data) => {
        setPois(data);
        if (resetPage) setCurrentPage(1);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        alert("Failed to load data");
      });
  };
  
  // ===== Fetch Stats =====
  const fetchStats = () => {
    fetch("http://127.0.0.1:5000/api/stats")
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Failed to fetch stats:", err));
  };
  
  useEffect(() => {
    fetchPois();
    fetchStats();
  }, []);

  // ===== Add new POI =====
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !city || !visits) {
      alert("Please fill all fields");
      return;
    }

    fetch(API_BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, city, visits: Number(visits) }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to add POI");
        return res.json();
      })
      .then(() => {
        setName("");
        setCity("");
        setVisits("");
        fetchPois();
        fetchStats();
      })
      .catch((err) => alert(err.message));
  };

  // ===== Delete POI =====
  const handleDelete = (id) => {
    if (!window.confirm("Delete this POI?")) return;

    fetch(`${API_BASE}/${id}`, { method: "DELETE" })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to delete");
        return res.json();
      })
      .then(() => {
        fetchPois(false);
        fetchStats();
      })      
      .catch((err) => alert(err.message));
  };

  // ===== Edit POI =====
  const handleEdit = (poi) => {
    setEditingId(poi.id);
    setEditName(poi.name);
    setEditCity(poi.city);
    setEditVisits(poi.visits);
  };

  const handleSave = (id) => {
    fetch(`${API_BASE}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: editName, city: editCity, visits: Number(editVisits) }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to update");
        return res.json();
      })
      .then(() => {
        setEditingId(null);
        fetchPois(false);
        fetchStats();
      })
      .catch((err) => alert(err.message));
  };

  const handleCancel = () => setEditingId(null);

  // ===== Sorting =====
  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  // ===== Filtering =====
  const filteredPois = pois.filter(
    (p) =>
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.city.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // ===== Sorting applied =====
  const sortedPois = [...filteredPois].sort((a, b) => {
    if (!sortColumn) return 0;
    const valA = a[sortColumn];
    const valB = b[sortColumn];
    if (typeof valA === "string") {
      const result = valA.localeCompare(valB);
      return sortDirection === "asc" ? result : -result;
    }
    return sortDirection === "asc" ? valA - valB : valB - valA;
  });

  // ===== Pagination =====
  const indexOfLast = currentPage * itemsPerPage;
  const indexOfFirst = indexOfLast - itemsPerPage;
  const currentPois = sortedPois.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(sortedPois.length / itemsPerPage);

  if (loading) return <h2>Loading...</h2>;

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>POI Dashboard</h1>
      {/* ===== Dashboard Section ===== */}
      {stats && (
        <div
          style={{
            display: "flex",
            gap: "2rem",
            marginBottom: "2rem",
            background: "#f8f9fa",
            padding: "1rem",
            borderRadius: "8px",
            justifyContent: "space-around",
          }}
        >
          <div>
            <strong>Total Visits:</strong> {stats.total_visits}
          </div>
          <div>
            <strong>Average Visits:</strong> {stats.avg_visits}
          </div>
          <div>
            <strong>Top City:</strong> {stats.top_city} ({stats.top_city_visits})
          </div>
        </div>
      )}

      {/* ===== Add new POI form ===== */}
      <form onSubmit={handleSubmit} style={{ marginBottom: "1.5rem", display: "flex", gap: "1rem" }}>
        <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
        <input placeholder="City" value={city} onChange={(e) => setCity(e.target.value)} />
        <input placeholder="Visits" type="number" value={visits} onChange={(e) => setVisits(e.target.value)} />
        <button type="submit">Add POI</button>
      </form>

      {/* ===== Search bar ===== */}
      <div style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Search by name or city..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ padding: "0.5rem", borderRadius: "6px", border: "1px solid #ccc", width: "250px" }}
        />
      </div>

      {/* ===== Table ===== */}
      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead style={{ backgroundColor: "#f0f0f0" }}>
          <tr>
            <th>ID</th>
            <th onClick={() => handleSort("name")} style={{ cursor: "pointer" }}>
              Name {sortColumn === "name" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
            </th>
            <th onClick={() => handleSort("city")} style={{ cursor: "pointer" }}>
              City {sortColumn === "city" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
            </th>
            <th onClick={() => handleSort("visits")} style={{ cursor: "pointer" }}>
              Visits {sortColumn === "visits" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {currentPois.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>
                {editingId === p.id ? (
                  <input value={editName} onChange={(e) => setEditName(e.target.value)} />
                ) : (
                  p.name
                )}
              </td>
              <td>
                {editingId === p.id ? (
                  <input value={editCity} onChange={(e) => setEditCity(e.target.value)} />
                ) : (
                  p.city
                )}
              </td>
              <td>
                {editingId === p.id ? (
                  <input type="number" value={editVisits} onChange={(e) => setEditVisits(e.target.value)} />
                ) : (
                  p.visits
                )}
              </td>
              <td>
                {editingId === p.id ? (
                  <>
                    <button style={{ backgroundColor: "#27ae60", color: "white" }} onClick={() => handleSave(p.id)}>
                      Save
                    </button>
                    <button onClick={handleCancel}>Cancel</button>
                  </>
                ) : (
                  <>
                    <button style={{ backgroundColor: "#2980b9", color: "white" }} onClick={() => handleEdit(p)}>
                      Edit
                    </button>
                    <button style={{ backgroundColor: "#c0392b", color: "white" }} onClick={() => handleDelete(p.id)}>
                      Delete
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* ===== Pagination ===== */}
      <div style={{ marginTop: "1rem", display: "flex", gap: "1rem", alignItems: "center" }}>
        <button onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))} disabled={currentPage === 1}>
          ◀ Previous
        </button>
        <span>
          Page {currentPage} of {totalPages}
        </span>
        <button onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))} disabled={currentPage === totalPages}>
          Next ▶
        </button>
        <select value={itemsPerPage} onChange={(e) => setItemsPerPage(Number(e.target.value))}>
          <option value={5}>5</option>
          <option value={10}>10</option>
          <option value={20}>20</option>
        </select>
      </div>
    </div>
  );
}

export default App;
