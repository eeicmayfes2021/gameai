/**
 * Constrain x to the range min to max.
 */
export const clamp = (x: number, min: number, max: number) => Math.max(Math.min(x, max), min);

export const isPhone = () =>
    window.matchMedia && window.matchMedia('(max-device-width: 560px)').matches;