// All calls to the FastAPI backend live here.
const BASE = "/api/irrigation";

function errorMessage(detail) {
  // FastAPI returns a string (our errors) or a list of {loc, msg} (validation errors).
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join("; ");
  }
  return "Unexpected error";
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Cannot reach the backend. Is uvicorn running on port 8000?");
  }
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      message = errorMessage((await response.json()).detail);
    } catch {
      /* keep default message */
    }
    throw new Error(message);
  }
  return response.json();
}

export const predict = (inputs) =>
  request("/predict", { method: "POST", body: JSON.stringify(inputs) });

export const getHistory = (limit = 50) => request(`/history?limit=${limit}`);

export const getMembershipFunctions = () => request("/membership-functions");
