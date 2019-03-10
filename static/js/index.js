var botAvatar =
  "https://robohash.org/liberovelitdolores.bmp?size=50x50&set=set1";
var userAvatar =
  "http://icons.iconarchive.com/icons/visualpharm/must-have/256/User-icon.png";

var telegram = new Vue({
  el: "#telegram",
  data: {
    botSleep: 1000,
    textfield: "",
    users: [
      { avatar: botAvatar, username: "Halmstad" },
      { avatar: userAvatar, username: "Wako", owner: true }
    ],
    messages: [
      {
        user: 0,
        text:
          "Hello, I'm a bot in a Messenger. I can be programmed without writing any code. Just use the node editor on the left"
      },
      {
        user: 0,
        text:
          "This example is a demonstration of [Rete.js](https://github.com/retejs/rete) framework. Based on it you can make your powerful editor"
      },
      {
        user: 0,
        text:
          "If you like the project, you can [support it](https://github.com/retejs/rete#donate)"
      }
    ]
  },
  methods: {
    formatMsg(msg) {
      return msg.replace(
        /\[(.+?)\]\((.+?)\)/g,
        '<a target="_blank" href="$2">$1</a>'
      );
    },
    onMessage() {
      var ms = this.$refs.messages;
      setTimeout(() => {
        ms.scrollTop = ms.scrollHeight;
      }, 100);
    },
    sendOwner(message) {
      this.messages.push({ user: 1, text: message });
      receiveBot(message);
      this.onMessage();
    },
    sendBot(message) {
      this.messages.push({ user: 0, text: message });
      this.onMessage();
    }
  }
});

var onMessageTask = [];
function receiveBot(msg) {
  setTimeout(async () => {
    await onMessageTask.map(t => t.run(msg));
  }, telegram.botSleep);
}

function receiveUser(msg) {
  telegram.sendBot(msg);
}

var actSocket = new Rete.Socket("Action");
var strSocket = new Rete.Socket("String");

const JsRenderPlugin = {
  install(editor, params = {}) {
    editor.on("rendercontrol", ({ el, control }) => {
      if (control.render && control.render !== "js") return;

      control.handler(el, editor);
    });
  }
};

class InputControl extends Rete.Control {
  constructor(key) {
    super();
    this.render = "js";
    this.key = key;
  }

  handler(el, editor) {
    var input = document.createElement("input");
    el.appendChild(input);

    var text = this.getData(this.key) || "Some message..";

    input.value = text;
    this.putData(this.key, text);
    input.addEventListener("change", () => {
      this.putData(this.key, input.value);
    });
  }
}

class MessageEventComponent extends Rete.Component {
  constructor() {
    super("Message event");
    this.task = {
      outputs: { act: "option", text: "output" },
      init(task) {
        onMessageTask.push(task);
    }
    };
  }

  builder(node) {
    var out1 = new Rete.Output("act", "Action", actSocket);
    var out2 = new Rete.Output("text", "Text", strSocket);
    return node.addOutput(out1).addOutput(out2);
  }

  worker(node, inputs, msg) {
    return { text: msg };
  }
}

class MessageSendComponent extends Rete.Component {
  constructor() {
    super("Message send");
    this.task = {
      outputs: {}
    };
  }

  builder(node) {
    var inp1 = new Rete.Input("act", "Action", actSocket, true);
    var inp2 = new Rete.Input("text", "Text", strSocket);

    var ctrl = new InputControl("text");
    inp2.addControl(ctrl);

    return node.addInput(inp1).addInput(inp2);
  }

  worker(node, inputs) {
    var text = inputs["text"] ? inputs["text"][0] : node.data.text; //default text
    console.log("msg send");
    receiveUser(text);
  }
}

class MessageMatchComponent extends Rete.Component {
  constructor() {
    super("Message match");
    this.task = {
      outputs: { t: "option", f: "option" }
    };
  }

  builder(node) {
    var inp1 = new Rete.Input("act", "Action", actSocket);
    var inp2 = new Rete.Input("text", "Text", strSocket);
    var out1 = new Rete.Output("t", "True", actSocket);
    var out2 = new Rete.Output("f", "False", actSocket);
    var ctrl = new InputControl("regexp");

    return node
      .addControl(ctrl)
      .addInput(inp1)
      .addInput(inp2)
      .addOutput(out1)
      .addOutput(out2);
  }
  worker(node, inputs) {
    var text = inputs["text"] ? inputs["text"][0] : "";

    if (!text.match(new RegExp(node.data.regexp, "gi"))) this.closed = ["t"];
    else this.closed = ["f"];
  }
}

class MessageComponent extends Rete.Component {
  constructor() {
    super("Message");
    this.task = {
      outputs: { text: "output" }
    };
  }

  builder(node) {
    var out = new Rete.Output("text", "Text", strSocket);
    var ctrl = new InputControl("text");

    return node.addControl(ctrl).addOutput(out);
  }

  worker(node, inputs) {
    return { text: node.data.text };
  }
}

var components = [
  new MessageEventComponent(),
  new MessageSendComponent(),
  new MessageMatchComponent(),
  new MessageComponent()
];

var container = document.getElementById("editor");
var editor = new Rete.NodeEditor("demo@0.1.0", container);
editor.use(VueRenderPlugin);
editor.use(ConnectionPlugin);
editor.use(ContextMenuPlugin);
editor.use(JsRenderPlugin);
editor.use(TaskPlugin);

var engine = new Rete.Engine("demo@0.1.0");

components.map(c => {
  editor.register(c);
  engine.register(c);
});

editor
  .fromJSON({
    id: "demo@0.1.0",
    nodes: {
      "1": {
        id: 1,
        data: {},
        group: null,
        inputs: {},
        outputs: {
          act: { connections: [{ node: 4, input: "act" }] },
          text: { connections: [{ node: 4, input: "text" }] }
        },
        position: [44, 138],
        name: "Message event"
      },
      "2": {
        id: 2,
        data: {},
        group: null,
        inputs: {
          act: { connections: [{ node: 4, output: "f" }] },
          text: { connections: [{ node: 3, output: "text" }] }
        },
        outputs: {},
        position: [673.2072854903905, 194.82554933538893],
        name: "Message send"
      },
      "3": {
        id: 3,
        data: { text: "ッ" },
        group: null,
        inputs: {},
        outputs: { text: { connections: [{ node: 2, input: "text" }] } },
        position: [334.3043696236001, 298.2715347978209],
        name: "Message"
      },
      "4": {
        id: 4,
        data: { regexp: ".*hello.*" },
        group: null,
        inputs: {
          act: { connections: [{ node: 1, output: "act" }] },
          text: { connections: [{ node: 1, output: "text" }] }
        },
        outputs: {
          t: { connections: [{ node: 5, input: "act" }] },
          f: { connections: [{ node: 2, input: "act" }] }
        },
        position: [333.40730287320383, 22.1000138522662],
        name: "Message match"
      },
      "5": {
        id: 5,
        data: {},
        group: null,
        inputs: {
          act: { connections: [{ node: 4, output: "t" }] },
          text: { connections: [{ node: 6, output: "text" }] }
        },
        outputs: {},
        position: [670.6284575254812, -103.66713461561366],
        name: "Message send"
      },
      "6": {
        id: 6,
        data: { text: "Hello!" },
        group: null,
        inputs: {},
        outputs: { text: { connections: [{ node: 5, input: "text" }] } },
        position: [317.85328833563574, -143.3955998177927],
        name: "Message"
      }
    },
    groups: {}
  })
  .then(() => {
    editor.on("error", err => {
      alertify.error(err.message);
    });

    editor.on(
      "process connectioncreated connectionremoved nodecreated",
      async function() {
        if (engine.silent) return;
        onMessageTask = [];
        console.log("process");
        await engine.abort();
        await engine.process(editor.toJSON());
      }
    );

    editor.trigger("process");
    editor.view.resize();
    AreaPlugin.zoomAt(editor);
  });