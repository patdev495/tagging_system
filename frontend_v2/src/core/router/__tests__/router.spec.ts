import { describe, it, expect, beforeEach } from 'vitest';
import router from '../index';

describe('Router Customer Isolation and Navigation', () => {
  beforeEach(async () => {
    localStorage.clear();
    sessionStorage.clear();
    await router.push('/');
  });

  it('navigates to / (CustomerSelect) by default when no customer is selected in localStorage', async () => {
    await router.push('/');
    expect(router.currentRoute.value.path).toBe('/');
    expect(router.currentRoute.value.name).toBe('CustomerSelect');
  });

  it('routes to /packing/ui for UI customer flow', async () => {
    localStorage.setItem('selected_customer', 'UI');
    await router.push('/packing/ui');
    expect(router.currentRoute.value.path).toBe('/packing/ui');
    expect(router.currentRoute.value.name).toBe('UIPacking');
  });

  it('routes to /packing/ux for UX customer weight-scale flow', async () => {
    localStorage.setItem('selected_customer', 'UX');
    await router.push('/packing/ux');
    expect(router.currentRoute.value.path).toBe('/packing/ux');
    expect(router.currentRoute.value.name).toBe('UXPacking');
  });

  it('always lands on / (CustomerSelect) on root path', async () => {
    localStorage.setItem('selected_customer', 'UI');
    await router.push('/');
    expect(router.currentRoute.value.path).toBe('/');
    expect(router.currentRoute.value.name).toBe('CustomerSelect');
  });
});

