import { NavLink, useLocation, useNavigate } from "react-router";
import { logout } from "../services/authService";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const token = sessionStorage.getItem("token");

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <nav
      className="navigation"
      aria-label="Main navigation"
      key={location.pathname}
    >
      {token ? (
        <>
          <NavLink to="/inventory">Inventory Dashboard</NavLink>
          <NavLink to="/stock">Stock Management</NavLink>
          <NavLink to="/transactions">
            Stock &amp; Transactions
          </NavLink>

          <button type="button" onClick={handleLogout}>
            Logout
          </button>
        </>
      ) : (
        <NavLink to="/login">Login</NavLink>
      )}
    </nav>
  );
}

export default Navbar;