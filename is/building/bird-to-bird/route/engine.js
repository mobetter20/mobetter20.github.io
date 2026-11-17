// Authored route rules. DOM, storage and presentation belong to app.js.
export function createRouteEngine(rounds, lexicon, saved = null) {
  if (!Array.isArray(rounds) || !rounds.length) throw new Error('The route pack is empty.');
  if (!Array.isArray(lexicon)) throw new Error('Invalid bird vocabulary.');

  const copyBird = bird => bird ? {...bird, parts: [...bird.parts]} : null;
  const copyRound = round => ({...round, parts: [...round.parts]});
  const birds = new Map();
  for (const bird of lexicon) {
    if (!bird || typeof bird.id !== 'string' || !bird.id || birds.has(bird.id) ||
        typeof bird.name !== 'string' || !Array.isArray(bird.parts) || !bird.parts.length ||
        ![...bird.parts].every(part => typeof part === 'string' && part)) {
      throw new Error('Invalid or duplicate bird entry.');
    }
    birds.set(bird.id, copyBird(bird));
  }

  const pack = [], graphs = new Map();
  for (const input of rounds) {
    if (!input || typeof input.id !== 'string' || !input.id || graphs.has(input.id) ||
        !Array.isArray(input.parts) || !input.parts.length ||
        ![...input.parts].every(part => typeof part === 'string' && part) ||
        new Set(input.parts).size !== input.parts.length) {
      throw new Error('Invalid or duplicate route round.');
    }
    const round = copyRound(input), start = birds.get(round.from), target = birds.get(round.to);
    if (!start || !target || start.id === target.id || start.parts.length !== 2 ||
        target.parts.length !== start.parts.length ||
        ![...start.parts, ...target.parts].every(part => round.parts.includes(part))) {
      throw new Error(`Invalid route endpoints: ${round.id}`);
    }
    const allowed = [...birds.values()].filter(bird => bird.parts.length === start.parts.length &&
      bird.parts.every(part => round.parts.includes(part)));
    // Neighbors retain the lexicon order. Distance never filters legal moves.
    const neighbors = new Map(allowed.map(bird => [bird.id, allowed.filter(other =>
      bird.parts.filter((part, index) => part !== other.parts[index]).length === 1
    ).map(other => other.id)]));
    const queue = [round.from], previous = new Map([[round.from, null]]);
    for (let index = 0; index < queue.length && !previous.has(round.to); index++) {
      for (const next of neighbors.get(queue[index])) {
        if (previous.has(next)) continue;
        previous.set(next, queue[index]);
        queue.push(next);
      }
    }
    if (!previous.has(round.to)) throw new Error(`Disconnected route endpoints: ${round.id}`);
    const solution = [round.to];
    while (solution[0] !== round.from) solution.unshift(previous.get(solution[0]));
    pack.push(round);
    graphs.set(round.id, {round, neighbors, solution, shortest: solution.length - 1});
  }

  let activeRoundId, states, bestPaths;
  const empty = round => ({path: [round.from], draft: []});
  const isWon = (id, state = states[id]) => state.path.at(-1) === graphs.get(id).round.to;
  function nextBirds(id, state) {
    if (isWon(id, state)) return [];
    return graphs.get(id).neighbors.get(state.path.at(-1)).map(birdId => birds.get(birdId));
  }
  function candidates(id, state) {
    return nextBirds(id, state)
      .filter(bird => state.draft.every((part, index) => bird.parts[index] === part));
  }
  function replacements(id, state) {
    const current = birds.get(state.path.at(-1));
    return nextBirds(id, state).map(bird => {
      const index = bird.parts.findIndex((part, index) => part !== current.parts[index]);
      return {bird, part: bird.parts[index], index};
    });
  }
  function validState(id, value) {
    if (!value || !Array.isArray(value.path) || !value.path.length || !Array.isArray(value.draft)) return null;
    const {round, neighbors} = graphs.get(id);
    const state = {path: [...value.path], draft: [...value.draft]};
    if (state.path[0] !== round.from || state.draft.length > birds.get(round.from).parts.length ||
        !state.draft.every(part => typeof part === 'string' && round.parts.includes(part))) return null;
    for (let index = 0; index < state.path.length; index++) {
      const current = state.path[index];
      if (!neighbors.has(current) || (index && !neighbors.get(state.path[index - 1]).includes(current)) ||
          (current === round.to && index !== state.path.length - 1)) return null;
    }
    if (state.draft.length && !candidates(id, state).length) return null;
    return state;
  }
  function restore(value) {
    states = Object.fromEntries(pack.map(round => [round.id, empty(round)]));
    bestPaths = Object.fromEntries(pack.map(round => [round.id, null]));
    activeRoundId = pack[0].id;
    if (!value || value.version !== 1) return false;
    for (const round of pack) {
      const state = validState(round.id, value.rounds?.[round.id]);
      if (state) states[round.id] = state;
      // A score is evidence of a completed legal route, never a trusted saved number.
      const best = validState(round.id, {path: value.rounds?.[round.id]?.bestPath, draft: []});
      if (best && isWon(round.id, best)) bestPaths[round.id] = best.path;
      rememberBest(round.id);
    }
    if (graphs.has(value.activeRoundId)) activeRoundId = value.activeRoundId;
    return true;
  }
  function rememberBest(id) {
    const state = states[id];
    if (isWon(id, state) && (!bestPaths[id] || state.path.length < bestPaths[id].length)) {
      bestPaths[id] = [...state.path];
    }
  }
  function view() {
    const state = states[activeRoundId], graph = graphs.get(activeRoundId);
    const available = candidates(activeRoundId, state), won = isWon(activeRoundId);
    const moves = state.path.length - 1;
    return {
      round: copyRound(graph.round), index: pack.findIndex(round => round.id === activeRoundId), total: pack.length,
      start: copyBird(birds.get(graph.round.from)), target: copyBird(birds.get(graph.round.to)),
      current: copyBird(birds.get(state.path.at(-1))), path: state.path.map(id => copyBird(birds.get(id))),
      draft: [...state.draft],
      eligible: [...new Set(available.map(bird => bird.parts[state.draft.length]).filter(Boolean))],
      replacements: replacements(activeRoundId, state).map(({part, index}) => ({part, index})),
      completeBird: copyBird(available.find(bird => bird.parts.length === state.draft.length)),
      moves, won, perfect: won && moves === graph.shortest,
      bestMoves: bestPaths[activeRoundId] ? bestPaths[activeRoundId].length - 1 : null,
      shortest: won ? graph.shortest : null,
      solution: won ? graph.solution.map(id => copyBird(birds.get(id))) : null,
      completed: pack.filter(round => isWon(round.id)).length,
    };
  }
  function selectPart(part) {
    if (!view().eligible.includes(part)) return false;
    states[activeRoundId].draft.push(part);
    return true;
  }
  function setReplacement(part) {
    const state = states[activeRoundId];
    const matches = replacements(activeRoundId, state).filter(choice => choice.part === part);
    if (matches.length !== 1) return false;
    const parts = matches[0].bird.parts;
    // Re-selecting the same pending bird is a no-op. The committed bird is the basis of every swap.
    if (state.draft.length === parts.length && parts.every((part, index) => state.draft[index] === part)) return false;
    state.draft = [...parts];
    return true;
  }
  function undoDraft() {
    if (!states[activeRoundId].draft.length) return false;
    states[activeRoundId].draft.pop();
    return true;
  }
  function clearDraft() {
    if (!states[activeRoundId].draft.length) return false;
    states[activeRoundId].draft = [];
    return true;
  }
  function commitBird() {
    const bird = view().completeBird;
    if (!bird) return false;
    states[activeRoundId].path.push(bird.id);
    states[activeRoundId].draft = [];
    rememberBest(activeRoundId);
    return true;
  }
  function goToRound(delta) {
    if (delta !== -1 && delta !== 1) return false;
    const index = pack.findIndex(round => round.id === activeRoundId) + delta;
    if (index < 0 || index >= pack.length) return false;
    activeRoundId = pack[index].id;
    return true;
  }
  function restartRound() {
    const state = states[activeRoundId];
    if (state.path.length === 1 && !state.draft.length) return false;
    states[activeRoundId] = empty(graphs.get(activeRoundId).round);
    return true;
  }
  function serialize() {
    return {version: 1, activeRoundId, rounds: Object.fromEntries(pack.map(round => [round.id, {
      path: [...states[round.id].path], draft: [...states[round.id].draft],
      ...(bestPaths[round.id] ? {bestPath: [...bestPaths[round.id]]} : {}),
    }]))};
  }
  restore(saved);
  return {view, serialize, restore, selectPart, setReplacement, undoDraft, clearDraft, commitBird, goToRound, restartRound};
}
