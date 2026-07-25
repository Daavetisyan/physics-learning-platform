(function attachRelativePositionPhysics(global) {
  const DIRECTION_MULTIPLIER = { right: 1, left: -1 };

  function displayedCoordinate(worldX, originWorldX, positiveDirection = 'right') {
    return DIRECTION_MULTIPLIER[positiveDirection] * (worldX - originWorldX);
  }

  function relativePosition(playerWorldX, referenceWorldX, positiveDirection = 'right') {
    return DIRECTION_MULTIPLIER[positiveDirection] * (playerWorldX - referenceWorldX);
  }

  function physicalDistance(firstWorldX, secondWorldX) {
    return Math.abs(firstWorldX - secondWorldX);
  }

  function formatSigned(value, unit = 'm') {
    const normalized = Math.abs(value) < 0.0001 ? 0 : value;
    const sign = normalized >= 0 ? '+' : '−';
    return `${sign}${Math.abs(normalized).toFixed(1)} ${unit}`;
  }

  function describeRelativePosition(playerWorldX, referenceWorldX, referenceLabel, positiveDirection = 'right') {
    const difference = playerWorldX - referenceWorldX;
    if (Math.abs(difference) < 0.05) {
      return `You and the ${referenceLabel.toLowerCase()} are at the same position.`;
    }
    const physicalDirection = difference > 0 ? 'right' : 'left';
    const signed = formatSigned(relativePosition(playerWorldX, referenceWorldX, positiveDirection));
    return `You are ${Math.abs(difference).toFixed(1)} m to the ${physicalDirection} of the ${referenceLabel.toLowerCase()} (${signed} with ${positiveDirection} positive).`;
  }

  function withinTolerance(actual, target, tolerance = 0.15) {
    return Math.abs(actual - target) <= tolerance;
  }

  function validateMission(mission, state) {
    const referenceWorldX = state.objects[state.selectedReference];
    const relative = relativePosition(state.playerWorldX, referenceWorldX, state.positiveDirection);
    const distance = physicalDistance(state.playerWorldX, referenceWorldX);
    switch (mission.type) {
      case 'physical_offset':
        return withinTolerance(state.playerWorldX - state.objects[mission.reference], mission.target, mission.tolerance);
      case 'distance':
        return state.selectedReference === mission.reference
          && withinTolerance(physicalDistance(state.playerWorldX, state.objects[mission.reference]), mission.target, mission.tolerance);
      case 'relative':
        return state.selectedReference === mission.reference && withinTolerance(relative, mission.target, mission.tolerance);
      case 'origin':
        return withinTolerance(state.originWorldX, state.objects[mission.reference], mission.tolerance);
      case 'direction':
        return state.positiveDirection === mission.direction;
      case 'tracking':
        return state.selectedReference === mission.reference && Math.abs(relative) <= mission.range;
      default:
        return false;
    }
  }

  global.RelativePositionPhysics = {
    displayedCoordinate,
    relativePosition,
    physicalDistance,
    formatSigned,
    describeRelativePosition,
    withinTolerance,
    validateMission,
  };
}(window));
