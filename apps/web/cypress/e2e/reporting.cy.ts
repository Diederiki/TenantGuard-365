/// <reference types="cypress" />

describe("Reporting dashboard", () => {
  beforeEach(() => {
    cy.setCookie("tg365_demo", "1");
  });

  it("renders KPI tiles", () => {
    cy.visit("/reporting");
    cy.contains("Reporting overview").should("be.visible");
    cy.contains("Total users").should("be.visible");
    cy.contains("Guest users").should("be.visible");
    cy.contains("Privileged admins").should("be.visible");
    cy.contains("Licenses").should("be.visible");
    cy.contains("Open alerts").should("be.visible");
  });

  it("renders all six chart cards", () => {
    cy.visit("/reporting");
    cy.contains("Audit volume (7d)").should("be.visible");
    cy.contains("Sign-in risk (7d)").should("be.visible");
    cy.contains("License utilisation").should("be.visible");
    cy.contains("Sharing-link risk distribution").should("be.visible");
    cy.contains("Alerts by severity").should("be.visible");
    cy.contains("Top SharePoint sites").should("be.visible");
  });

  it("data source badge surfaces (live or demo)", () => {
    cy.visit("/reporting");
    cy.contains(/data: (live|demo)/i).should("be.visible");
  });

  it("top-site row links to SharePoint sites", () => {
    cy.visit("/reporting");
    cy.contains("a", "/sites/engineering").should("have.attr", "href", "/sharepoint/sites");
  });
});
