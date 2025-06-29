/* utils/auth.ts ****************************************************/
/* “use client” forces a client bundle so we can call localStorage. */
"use client"

import { redirect } from "next/navigation"
import { ApiError } from "./api-error"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://skill-forge-b-ackend.vercel.app"
const TOKEN_KEY = "skill_forge_auth_token"
const USER_EMAIL_KEY = "skill_forge_user_email"

export const setAuthToken = (token, email) => {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_EMAIL_KEY, email)
  }
}

export const getAuthToken = () =>
  typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null

export const getUserEmail = () =>
  typeof window !== "undefined" ? localStorage.getItem(USER_EMAIL_KEY) : null

export const removeAuthToken = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_EMAIL_KEY)
  }
}

// Helper function for making POST requests with standardized error handling
const postWithAuthErrorHandling = async (path, body) => {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      mode: "cors",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      let errorData = {}
      try { errorData = await response.json() } catch {}
      const apiMsg = errorData.detail || errorData.message
      if (apiMsg) throw new ApiError(apiMsg, response.status)
      let genericMessage = "An unknown API error occurred."
      if (response.status >= 400 && response.status < 500) {
        genericMessage = "Bad Request"
      } else if (response.status >= 500 && response.status < 600) {
        genericMessage = "Server Error"
      }
      throw new ApiError(genericMessage, response.status)
    }
    return response.json()
  } catch (err) {
    if (err instanceof ApiError) {
      throw err
    } else if (err instanceof TypeError && err.message === "Failed to fetch") {
      throw new ApiError("Failed to connect to server. Please check your internet connection.", 0)
    } else {
      throw new ApiError("An unexpected error occurred during the request.", -1)
    }
  }
}

export const registerUser = (email, password) =>
  postWithAuthErrorHandling("/auth/Register", { email, password })

export const loginUser = async (email, password) => {
  const data = await postWithAuthErrorHandling("/auth/Login", { email, password })
  setAuthToken(data.token || data.access_token, email)
  return data
}

export const protectedFetch = async (path, init = {}) => {
  const token = getAuthToken()
  if (!token) {
    if (typeof window !== "undefined") redirect("/auth/login")
    return Promise.reject("Unauthenticated")
  }

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      mode: "cors",
      headers: {
        ...(init.headers ?? {}),
        Authorization: `Bearer ${token}`,
      },
    })

    if (response.status === 401) {
      removeAuthToken()
      if (typeof window !== "undefined") redirect("/auth/login")
      return Promise.reject("Token expired")
    }

    if (!response.ok) {
      let errorData = {}
      try { errorData = await response.json() } catch {}
      const apiMsg = errorData.detail || errorData.message
      if (apiMsg) throw new ApiError(apiMsg, response.status)
      let genericMessage = "An unknown API error occurred."
      if (response.status >= 400 && response.status < 500) {
        genericMessage = "Bad Request"
      } else if (response.status >= 500 && response.status < 600) {
        genericMessage = "Server Error"
      }
      throw new ApiError(genericMessage, response.status)
    }

    return response.json()
  } catch (err) {
    if (err instanceof ApiError) {
      throw err
    } else if (err instanceof TypeError && err.message === "Failed to fetch") {
      throw new ApiError("Failed to connect to server. Please check your internet connection.", 0)
    } else {
      throw new ApiError("An unexpected error occurred during the request.", -1)
    }
  }
}
