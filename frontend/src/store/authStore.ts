import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { supabase, safeStorage } from "../lib/supabase";

export interface User {
    id: string;
    email: string;
    username: string;
    role: string;
    created_at?: string;
    updated_at?: string;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    isInitialized: boolean;
    error: string | null;

    login: (credentials: any) => Promise<void>;
    register: (data: any) => Promise<void>;
    loginWithGoogle: () => Promise<void>;
    loginWithGithub: () => Promise<void>;
    logout: () => Promise<void>;
    clearError: () => void;
    initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            isInitialized: false,
            error: null,

            initialize: async () => {
                const { data: { session } } = await supabase.auth.getSession();
                if (session) {
                    // Fetch profile details
                    const { data: profile } = await supabase
                        .from('profiles')
                        .select('*')
                        .eq('id', session.user.id)
                        .maybeSingle();

                    set({
                        token: session.access_token,
                        isAuthenticated: true,
                        isInitialized: true,
                        user: profile ? {
                            id: session.user.id,
                            email: session.user.email || "",
                            username: profile.username || "User",
                            role: profile.role || "analyst"
                        } : {
                            id: session.user.id,
                            email: session.user.email || "",
                            username: session.user.user_metadata?.full_name || session.user.user_metadata?.user_name || "User",
                            role: "analyst"
                        }
                    });
                } else {
                    set({ isInitialized: true, isAuthenticated: false, token: null, user: null });
                }

                // Listen for auth changes
                supabase.auth.onAuthStateChange((_event, session) => {
                    if (session) {
                        set({ token: session.access_token, isAuthenticated: true });
                    } else {
                        set({ token: null, isAuthenticated: false, user: null });
                    }
                });
            },

            login: async ({ email, password }) => {
                set({ isLoading: true, error: null });
                try {
                    const { data, error } = await supabase.auth.signInWithPassword({
                        email,
                        password,
                    });

                    if (error) throw error;

                    const { data: profile } = await supabase
                        .from('profiles')
                        .select('*')
                        .eq('id', data.user.id)
                        .maybeSingle();

                    set({
                        token: data.session.access_token,
                        isAuthenticated: true,
                        user: profile ? {
                            id: data.user.id,
                            email: data.user.email || "",
                            username: profile.username || "User",
                            role: profile.role || "analyst"
                        } : {
                            id: data.user.id,
                            email: data.user.email || "",
                            username: data.user.user_metadata?.full_name || data.user.user_metadata?.user_name || "User",
                            role: "analyst"
                        },
                        isLoading: false,
                    });
                } catch (error: any) {
                    set({
                        error: error.message || "Failed to login. Please check your credentials.",
                        isLoading: false,
                    });
                    throw error;
                }
            },

            loginWithGoogle: async () => {
                set({ isLoading: true, error: null });
                try {
                    const { error } = await supabase.auth.signInWithOAuth({
                        provider: 'google',
                        options: {
                            redirectTo: `${window.location.origin}/dashboard`,
                        },
                    });
                    if (error) throw error;
                } catch (error: any) {
                    set({
                        error: error.message || "Failed to login with Google.",
                        isLoading: false,
                    });
                    throw error;
                }
            },

            loginWithGithub: async () => {
                set({ isLoading: true, error: null });
                try {
                    const { error } = await supabase.auth.signInWithOAuth({
                        provider: 'github',
                        options: {
                            redirectTo: `${window.location.origin}/dashboard`,
                        },
                    });
                    if (error) throw error;
                } catch (error: any) {
                    set({
                        error: error.message || "Failed to login with GitHub.",
                        isLoading: false,
                    });
                    throw error;
                }
            },

            register: async ({ email, password, username }) => {
                set({ isLoading: true, error: null });
                try {
                    // Call our Fast API Gateway instead of Supabase directly
                    const response = await fetch("http://localhost:8000/api/v1/auth/register", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, password, username })
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || "Registration failed via Gateway");
                    }

                    // The Gateway created the Auth User AND the Profile row securely.
                    // Now we perform a standard login to get the active session token!
                    const loginResponse = await supabase.auth.signInWithPassword({
                        email,
                        password,
                    });

                    if (loginResponse.error) throw loginResponse.error;

                    set({
                        token: loginResponse.data.session.access_token,
                        isAuthenticated: true,
                        user: {
                            id: loginResponse.data.user.id,
                            email: email,
                            username: username,
                            role: "analyst"
                        },
                        isLoading: false,
                    });

                } catch (error: any) {
                    set({
                        error: error.message || "Registration failed. Please try again.",
                        isLoading: false,
                    });
                    throw error;
                }
            },

            logout: async () => {
                await supabase.auth.signOut();
                set({ user: null, token: null, isAuthenticated: false });
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: "auth-storage",
            storage: createJSONStorage(() => safeStorage),
            partialize: (state) => ({ token: state.token, isAuthenticated: state.isAuthenticated, user: state.user }),
        }
    )
);
