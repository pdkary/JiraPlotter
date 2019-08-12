import { Board } from './Board'
import { Analysis } from './Analysis';

export class AnalysisWrapper {
    boards: Map<String,Board>;
    analysis: Analysis;
}