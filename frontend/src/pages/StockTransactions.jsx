import { useEffect, useState } from "react";
import ProductTable from "../components/ProductTable";
import {
  getLowStockProducts,
  getTransactions,
} from "../services/inventoryService";

function StockTransactions() {
  const [lowStockProducts, setLowStockProducts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadCount, setReloadCount] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function loadData() {
      setLoading(true);
      setError("");

      try {
        const [productData, transactionData] = await Promise.all([
          getLowStockProducts(),
          getTransactions(),
        ]);

        if (!ignore) {
          setLowStockProducts(productData);
          setTransactions(transactionData);
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

    loadData();

    return () => {
      ignore = true;
    };
  }, [reloadCount]);

  return (
    <section className="card">
      <h2>Stock &amp; Transactions</h2>
      <p>View low-stock products and recorded stock movements.</p>

      <button
        type="button"
        onClick={() => setReloadCount((count) => count + 1)}
        disabled={loading}
      >
        {loading ? "Loading..." : "Refresh Data"}
      </button>

      {loading && <p role="status">Loading stock information...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!loading && !error && (
        <>
          <h3>Low-stock Products</h3>

          {lowStockProducts.length > 0 ? (
            <ProductTable products={lowStockProducts} />
          ) : (
            <p>No products are currently low in stock.</p>
          )}

          <h3>Transaction History</h3>

          {transactions.length > 0 ? (
           <div
           className="table-wrapper"
           role="region"
           aria-label="Product stock table"
           tabIndex={0}
           >
              <table>
                <caption>Recorded stock receipts and issues</caption>

                <thead>
                  <tr>
                    <th scope="col">ID</th>
                    <th scope="col">Product</th>
                    <th scope="col">SKU</th>
                    <th scope="col">Type</th>
                    <th scope="col">Quantity</th>
                    <th scope="col">Supplier</th>
                    <th scope="col">Recorded By</th>
                    <th scope="col">Date</th>
                  </tr>
                </thead>

                <tbody>
                  {transactions.map((transaction) => (
                    <tr key={transaction.id}>
                      <td>{transaction.id}</td>
                      <td>{transaction.product_name}</td>
                      <td>{transaction.sku}</td>
                      <td>{transaction.transaction_type}</td>
                      <td>{transaction.quantity}</td>
                      <td>{transaction.supplier_name || "—"}</td>
                      <td>{transaction.username}</td>
                      <td>
                        {new Date(
                          transaction.transaction_date
                        ).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No stock transactions have been recorded yet.</p>
          )}
        </>
      )}
    </section>
  );
}

export default StockTransactions;