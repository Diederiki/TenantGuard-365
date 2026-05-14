/// <reference types="cypress" />

/**
 * Smoke tests. Run against a built Next.js server in demo mode.
 *
 * Prereq: web server reachable at CYPRESS_BASE_URL (default http://localhost:3000).
 * The tg365_demo=1 cookie is set by `visitDemo`, so the dashboard renders
 * without a live API.
 */
describe("Smoke — demo mode", () => {
  it("dashboard renders", () => {
    cy.visitDemo("/");
    cy.contains(/TenantGuard|M365 Control Center|Overview|Dashboard/i, {
      timeout: 12000,
    }).should("be.visible");
  });

  it("audit log loads with MUI DataGrid", () => {
    cy.visitDemo("/audit");
    cy.contains("Technician audit log").should("be.visible");
    cy.get(".MuiDataGrid-root", { timeout: 12000 }).should("be.visible");
    cy.get(".MuiDataGrid-row").its("length").should("be.greaterThan", 0);
  });

  it("entra users grid loads", () => {
    cy.visitDemo("/entra/users");
    cy.contains("Directory users").should("be.visible");
    cy.get(".MuiDataGrid-root").should("be.visible");
  });

  it("sharepoint permissions grid loads", () => {
    cy.visitDemo("/sharepoint/permissions");
    cy.contains("Permissions audit").should("be.visible");
    cy.get(".MuiDataGrid-root").should("be.visible");
  });

  it("settings index renders cards", () => {
    cy.visitDemo("/settings");
    cy.contains(/Settings/i).should("be.visible");
    cy.contains(/Graph/i).should("be.visible");
  });

  it("settings → graph form renders fields", () => {
    cy.visitDemo("/settings/graph");
    cy.contains("Test connection").should("be.visible");
    cy.contains(/Save settings/i).should("be.visible");
  });

  it("totp enroll page renders QR or URI", () => {
    cy.visitDemo("/settings/users/00000000-0000-0000-0000-000000000001/totp");
    // Demo mode renders the fake otpauth URI immediately.
    cy.contains(/otpauth:/, { timeout: 10000 }).should("exist");
  });

  it("sidebar links navigate", () => {
    cy.visitDemo("/");
    cy.contains("a", "Audit log").click();
    cy.url().should("include", "/audit");
    cy.contains("Technician audit log").should("be.visible");
  });
});
