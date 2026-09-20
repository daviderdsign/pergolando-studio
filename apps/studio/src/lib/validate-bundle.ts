import { catalogDatabaseSchema, priceMatricesSchema } from "@pergolando/shared/schema";
import { checkPriceMatrices, type CoherenceIssue } from "./matrix-coherence";
import { runSmokeTests, type SmokeTestResult } from "./regression-harness";
import type { Draft } from "./storage";

export interface ValidationReport {
  schemaValid: boolean;
  schemaErrors: string[];
  coherenceIssues: CoherenceIssue[];
  smokeTests: SmokeTestResult[];
  /** Export is blocked unless this is true (STU-5, "revisione umana obbligatoria"). */
  passed: boolean;
}

export function validateDraft(draft: Draft): ValidationReport {
  const dbResult = catalogDatabaseSchema.safeParse(draft.database);
  const pmResult = priceMatricesSchema.safeParse(draft.priceMatrices);

  const schemaErrors: string[] = [];
  if (!dbResult.success) {
    schemaErrors.push(
      ...dbResult.error.issues.map((i) => `catalog/database.json: ${i.path.join(".")}: ${i.message}`),
    );
  }
  if (!pmResult.success) {
    schemaErrors.push(
      ...pmResult.error.issues.map(
        (i) => `catalog/price_matrices.json: ${i.path.join(".")}: ${i.message}`,
      ),
    );
  }

  const schemaValid = dbResult.success && pmResult.success;

  const coherenceIssues =
    pmResult.success ? checkPriceMatrices(pmResult.data as Parameters<typeof checkPriceMatrices>[0]) : [];
  const smokeTests =
    dbResult.success && pmResult.success ? runSmokeTests(dbResult.data, pmResult.data) : [];

  const hasBlockingCoherenceIssues = coherenceIssues.some((i) => i.severity === "error");
  const hasFailingSmokeTests = smokeTests.some((t) => !t.ok);

  return {
    schemaValid,
    schemaErrors,
    coherenceIssues,
    smokeTests,
    passed: schemaValid && !hasBlockingCoherenceIssues && !hasFailingSmokeTests,
  };
}
