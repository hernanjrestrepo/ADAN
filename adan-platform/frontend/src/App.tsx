import { Navigate, Route, Routes } from "react-router-dom";

import { Agents } from "./pages/Agents";
import { Dashboard } from "./pages/Dashboard";
import { KGExplorer } from "./pages/KGExplorer";
import { Login } from "./pages/Login";

function isAuthenticated(): boolean {
  return localStorage.getItem("adan_token") !== null;
}

function PrivateRoute({ children }: { children: JSX.Element }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/agents"
        element={
          <PrivateRoute>
            <Agents />
          </PrivateRoute>
        }
      />
      <Route
        path="/kg"
        element={
          <PrivateRoute>
            <KGExplorer />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
