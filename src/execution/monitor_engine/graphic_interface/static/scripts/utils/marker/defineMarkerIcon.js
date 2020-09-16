import { eventIcons, actorIcons } from './markerIcons.js';

function checkVictimLifetime(lifetime) {
    if (lifetime === 0) {
        return eventIcons.victim.icon3;
    } else if (lifetime < 5) {
        return eventIcons.victim.icon2;
    } else if (lifetime < 10) {
        return eventIcons.victim.icon1;
    }
    
    return eventIcons.victim.icon0;
}

export function defineEventIcon(event) {
    if (event['type'] === 'victim') {
        return checkVictimLifetime(event['lifetime']);
    }
    
    return eventIcons[event['type']];
}

export function defineActorIcon(actor) {
    if (actor['type'] === 'agent') {
        return actorIcons.roles[actor['role']];
    }
    
    return actorIcons.professions[actor['profession']];
}