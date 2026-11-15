import { useEffect, useState } from "react";
import ProductTable from "../components/ProductTable";
import {
  getProducts,
  getSuppliers,
} from "../services/inventoryService";

function InventoryDashboard() {
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadCount, setReloadCount] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [productData, supplierData] = await Promise.all([
          getProducts(),
          getSuppliers(),
        ]);

        if (!ignore) {
          setProducts(productData);
          setSuppliers(supplierData);
        }
      } catch (error) {
        if (!ignore) {
          setError(error.message);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      ignore = true;
    };
  }, [reloadCount]);

  return (
    <section className="card">
      <h2>Inventory Dashboard</h2>
      <p>View current inventory and supplier information.</p>

      <button
        type="button"
        onClick={() => setReloadCount((count) => count + 1)}
        disabled={loading}
      >
        {loading ? "Loading..." : "Refresh Data"}
      </button>

      {loading && <p role="status">Loading inventory...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && (
        <>
          <h3>Products</h3>

          {products.length > 0 ? (
            <ProductTable products={products} />
          ) : (
            <p>No products found.</p>
          )}

          <h3>Suppliers</h3>

          {suppliers.length > 0 ? (
            <ul>
              {suppliers.map((supplier) => (
                <li key={supplier.id}>
                  {supplier.supplier_name} ({supplier.supplier_code})
                </li>
              ))}
            </ul>
          ) : (
            <p>No suppliers found.</p>
          )}
        </>
      )}
    </section>
  );
}

export default InventoryDashboard;