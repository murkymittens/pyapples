var socket = null;
var chat = null;
var wsurl = "ws://localhost:8888";
var session_id = null;
var game_input_group = null;
var chat_input_group = null;
var name_input_group = null;
var game_input = null;
var chat_input = null;
var name_input = null;
var my_name = null;
var current_round_judge = null;
var game_name = null;
var red_card_template = null;
var player_cards = null;
var judge_name = null;
var green_card_word = null;
var green_card_synonyms = null;

$(function() {
	chat = $("#chat");
	game_input_group = $("#game_input_group");
	chat_input_group = $("#chat_input_group");
	name_input_group = $("#name_input_group");
	game_input = $("#game_input");
	name_input = $("#name_input");
	chat_input = $("#chat_input");
	red_card_template = $("#red-apple-template");
	player_cards = $("#player-cards");
	judge_name = $("#judge-name");
	green_card_word = $("#green-card-word");
	green_card_synonyms = $("#green-card-synonyms");

	game_input_group.hide();
	chat_input_group.hide();

	connect();
});

function connect() {
	socket = new WebSocket(wsurl);

	if(socket) {
		socket.onopen = onConnectionOpen;
		socket.onclose = onConnectionClosed;
		socket.onmessage = onMessageReceived;
	}
}

function onMessageReceived(event) {
	var message = $.parseJSON(event.data);
	switch(message.type) {
		case 0: // system message
			append_chat("SYSTEM", message.payload);
			break;
		case 1: // receive session id
			session_id = message.payload;
			append_chat("SYSTEM", "Got session id: " + session_id);
			break;
		case 8: // join game success
		case 4: // create game success
			append_chat("SYSTEM", "Joined game: " + message.payload);
			break;
		case 9: // failed to join game
			sendMessage(3, game_name);
			break;
		case 12: // player's red apple cards
			append_chat("GAME", "Got my red apples: " + message.payload.length);
			console.log("red apples: %o", message.payload);
			clear_red_cards();
			for(var i=0; i<message.payload.length; i++) {
				make_red_card(message.payload[i].word, message.payload[i].flavour, i);
			}
			break;
		case 11: // round details
			append_chat("GAME", "Got round details");
			console.log("round details: %o", message.payload);
			judge_name.html(message.payload.JUDGE);
			current_round_judge = message.payload.JUDGE;
			green_card_word.html(message.payload.GREEN_APPLE.word);
			green_card_synonyms.html(message.payload.GREEN_APPLE.flavour);
			break;
		case 13: // red cards to judge
			append_chat("GAME", "Got apples to judge");
			clear_red_cards();
			for(var card_index in message.payload) {
				make_red_card(message.payload[card_index].word, message.payload[card_index].flavour, card_index);
			}
			break;
		default:
			console.log("type: %d\ndata: %o", message.type, message.payload);
			break;
	}
}

function onConnectionOpen() {
	append_chat("LOCAL", "Connected to server.");
}

function onConnectionClosed(event) {
	append_chat("LOCAL", "Disconnected from server.");
}

function sendMessage(messageType, messagePayload) {
	if(socket) {
		append_chat("LOCAL", "Sending: " + messageType);
		var json = {type: messageType, payload: messagePayload};
		var encoded = $.toJSON(json);
		socket.send(encoded);
	} else {
		append_chat("LOCAL", "Not connected...");
	}
}

function play_red_card(element) {
	var red_card_index = $(element).attr('data-card-index');
	//alert("Red card index: " + red_card_index);
	if(current_round_judge == my_name) {
		var type = 16;
	} else {
		var type = 15;
	}
	sendMessage(type, red_card_index);
}

function start_round() {
	sendMessage(14, '');
}

function submit_name() {
	my_name = name_input.val();
	sendMessage(6, my_name);
	name_input_group.hide();
	game_input_group.show();
}

function submit_game() {
	game_name = game_input.val();
	sendMessage(7, game_name);
	game_input_group.hide();
	chat_input_group.show();
}

function submit_chat() {
	var chat = chat_input.val();
	chat_input.val("");
	chat_input_group
}

function append_chat(prefix, message) {
	chat.append("<div><b>" + prefix + ":</b> " + message + "</div>");
	chat.scrollTop(chat[0].scrollHeight);
}

function clear_red_cards() {
	player_cards.find(".red-apple[id!='red-apple-template']").remove();
}

function make_red_card(word, flavour, index) {
	var card = red_card_template.clone();
	card.removeAttr('id');
	card.removeClass('hidden');
	card.attr('data-card-index', index);
	card.find(".media-heading").eq(0).html(word);
	card.find(".text-right").eq(0).html(flavour);
	player_cards.append(card);
}