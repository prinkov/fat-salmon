/* eslint-disable prettier/prettier */
export {};

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
        initDataUnsafe?: any;
        version?: string;
        platform?: string;
        colorScheme?: string;
        isExpanded?: boolean;
        expand?: () => void;
        ready?: () => void;
        close?: () => void;
        MainButton?: any;
        BackButton?: any;
        showAlert?: (message: string, callback?: (ok: boolean) => void) => void;
        showConfirm?: (message: string, callback?: (ok: boolean) => void) => void;
        [key: string]: any;
      };
    };
  }
}
