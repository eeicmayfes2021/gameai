/**
 * Constrain x to the range min to max.
 */
export const clamp = (x: number, min: number, max: number) => Math.max(Math.min(x, max), min);
