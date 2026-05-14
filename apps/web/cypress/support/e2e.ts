/// <reference types="cypress" />

// Custom command: visit a path with demo cookie pre-set so we skip API calls.
Cypress.Commands.add("visitDemo", (path: string) => {
  cy.setCookie("tg365_demo", "1");
  cy.visit(path);
});

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Cypress {
    interface Chainable {
      visitDemo(path: string): Chainable<void>;
    }
  }
}

export {};
