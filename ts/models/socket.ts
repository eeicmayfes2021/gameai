import { Stone } from './common';

export interface MoveStonesMessage {
    stones: Stone[];
}

export interface WinMessage {
    score: number;
}
