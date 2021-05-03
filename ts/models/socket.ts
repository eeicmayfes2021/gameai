import { Stone } from './common';

export interface MoveStonesMessage {
    stones: Stone[];
}

export interface WinMessage {
    score: number;
}

export interface ModelMessage {
    model_path: string;
}

export interface LeftMessage {
    left: number;
}
