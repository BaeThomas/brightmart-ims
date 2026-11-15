import { Routes, Route, Navigate, Link } from "react-router";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import InventoryDashboard from "./pages/InventoryDashboard";
import StockManagement from "./pages/StockManagement";
import StockTransactions from "./pages/StockTransactions";
import "./App.css";

function App() {
  return (
    <div className="container">
      <header className="page-header">
        <h1>BrightMart IMS</h1>
        <p>Inventory Management System</p>
      </header>

      <Navbar />

      <main>
        <Routes>
          <Route
            path="/"
            element={<Navigate to="/inventory" replace />}
          />

          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute />}>
            <Route
              path="/inventory"
              element={<InventoryDashboard />}
            />
            <Route path="/stock" element={<StockManagement />} />
            <Route
              path="/transactions"
              element={<StockTransactions />}
            />
          </Route>

          <Route
            path="*"
            element={
              <section className="card">
                <h2>Page not found</h2>
                <p>The page you requested does not exist.</p>
                <Link to="/inventory">
                  Go to Inventory Dashboard
                </Link>
              </section>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;