/**
 * Constrain x to the range min to max.
 * @param {number} x 
 * @param {number} min 
 * @param {number} max 
 */
export const clamp = (x, min, max) => Math.max(Math.min(x, max), min);
