import { useEffect, useState } from "react";
import ProductTable from "../components/ProductTable";
import { getProducts, getSuppliers } from "../services/inventoryService";

function InventoryDashboard() {
  const [products, setProducts] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadCount, setReloadCount] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");

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

  const totalProducts = products.length;

  const totalAvailableStock = products.reduce(
    (total, product) => total + Number(product.stock_quantity),
    0
  );

  const lowStockCount = products.filter(
    (product) => Number(product.stock_quantity) <= Number(product.reorder_level)
  ).length;

  const categoryNames = [
    ...new Set(products.map((product) => product.category_name).filter(Boolean)),
  ].sort();

  const query = searchTerm.trim().toLowerCase();

  const filteredProducts = products.filter((product) => {
    const name = (product.product_name ?? "").toLowerCase();
    const sku = (product.sku ?? "").toLowerCase();

    const matchesSearch = name.includes(query) || sku.includes(query);
    const matchesCategory =
      selectedCategory === "" || product.category_name === selectedCategory;

    return matchesSearch && matchesCategory;
  });

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
          <section aria-labelledby="inventory-summary-heading">
            <h3 id="inventory-summary-heading">Inventory Summary</h3>

            <dl className="inventory-summary">
              <div>
                <dt>Total products</dt>
                <dd>{totalProducts}</dd>
              </div>

              <div>
                <dt>Total available units</dt>
                <dd>{totalAvailableStock}</dd>
              </div>

              <div>
                <dt>Low-stock products</dt>
                <dd>{lowStockCount}</dd>
              </div>
            </dl>
          </section>

          <h3>Products</h3>

          <div className="inventory-filters">
            <label>
              Search by product name or SKU
              <input
                type="search"
                placeholder="Enter a product name or SKU"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
              />
            </label>

            <label>
              Category
              <select
                value={selectedCategory}
                onChange={(event) => setSelectedCategory(event.target.value)}
              >
                <option value="">All categories</option>
                {categoryNames.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {filteredProducts.length > 0 ? (
            <ProductTable products={filteredProducts} />
          ) : (
            <p role="status">
              {products.length === 0
                ? "No products found."
                : "No products match your search or selected category."}
            </p>
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