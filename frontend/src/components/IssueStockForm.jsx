import { useState } from "react";
import { issueStock } from "../services/inventoryService";

function IssueStockForm({ products, onStockUpdated }) {
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const selectedProduct = products.find(
    (product) => product.id === Number(productId)
  );

  async function handleIssue(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const amount = Number(quantity);

    if (!selectedProduct) {
      setError("Please select a product.");
      return;
    }

    if (!Number.isSafeInteger(amount) || amount <= 0) {
      setError("Quantity must be a positive whole number.");
      return;
    }

    if (amount > selectedProduct.stock_quantity) {
      setError("Quantity cannot exceed the available stock.");
      return;
    }

    setSaving(true);

    try {
      const transaction = await issueStock({
        product: Number(productId),
        quantity: amount,
      });

      setSuccess(
        `Issued ${transaction.quantity} units successfully. ` +
        `Transaction ID: ${transaction.id}.`
      );

      setQuantity("");

      try {
        await onStockUpdated();
      } catch {
        setError(
          "Stock was issued, but the latest stock could not be loaded. " +
          "Reload the page to check it. Do not submit the same issue again."
        );
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="stock-section">
      <h3>Issue Stock</h3>
      <p>Record stock leaving the inventory.</p>

      {products.length === 0 ? (
        <p>No products are available.</p>
      ) : (
        <form onSubmit={handleIssue} className="form">
          <label htmlFor="issue-product">Product</label>
          <select
            id="issue-product"
            value={productId}
            onChange={(event) => setProductId(event.target.value)}
            disabled={saving}
            required
          >
            <option value="">Select a product</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.product_name} ({product.sku})
              </option>
            ))}
          </select>

          {selectedProduct && (
            <p>
              Current stock:{" "}
              <strong>{selectedProduct.stock_quantity}</strong>
            </p>
          )}

          <label htmlFor="issue-quantity">Quantity</label>
          <input
            id="issue-quantity"
            type="number"
            min="1"
            step="1"
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
            disabled={saving}
            required
          />

          <button type="submit" disabled={saving}>
            {saving ? "Issuing..." : "Issue Stock"}
          </button>
        </form>
      )}

      {success && (
        <p className="success-message" role="status">
          {success}
        </p>
      )}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}

export default IssueStockForm;