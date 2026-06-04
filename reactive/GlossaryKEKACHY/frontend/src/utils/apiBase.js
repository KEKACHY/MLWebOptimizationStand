const defaultBase = `${window.location.protocol}//${window.location.hostname}:8020`;

export const apiBase = import.meta.env.VITE_API_BASE || defaultBase;

export const apiUrl = (path) => new URL(path, apiBase).toString();
