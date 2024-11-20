import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { PageConfig } from '@jupyterlab/coreutils';
import { ICommandPalette, ToolbarButton } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { NotebookPanel, NotebookActions } from '@jupyterlab/notebook';
import { ICellModel } from '@jupyterlab/cells';
import { requestAPI } from './handler';
import { createAlert } from './alert';
import $ from 'jquery';


function ImgCmdInit(tracker: INotebookTracker): void {
  
  const images = document.querySelectorAll('img');
  const baseURL = PageConfig.getBaseUrl();
  const controller = new AbortController;
  
  document.querySelector('div.success') ?? createAlert(document,"Figure saved", ["alert-box", "success"]);
  document.querySelector('div.info') ?? createAlert(document,"Press Esc to exit figure selection mode", ["alert-box", "info"]);
  
  $("div.info").fadeIn( 300 );

  images.forEach((image) => {

    image.style.border = '5px solid transparent';

    // Add mouseover event to highlight the image
    image.addEventListener('mouseover', function addBorder(){
      image.style.border = '5px solid blue'; // Change border to highlight
    }, { signal: controller.signal });

    // Add mouseout event to remove highlight
    image.addEventListener('mouseout', function rmBorder(){
      image.style.border = '5px solid transparent'; // Reset the border
    }, { signal: controller.signal });
    // Add click event to save image to cache
    image.addEventListener('click', function saveImg(){
      let par = image.closest('div.jp-CodeCell');
      let idx = par?.attributes?.getNamedItem('data-windowed-list-index')?.value;
      let nb = tracker.currentWidget;
      let p_cell = idx ? nb?.model?.cells.get(Number(idx)) as ICellModel:null;
      let p_code = p_cell?.toJSON();
      let b = JSON.stringify({"p_code": p_code, "src": image.src});
      console.log(b);
      requestAPI(`${baseURL}img`, {
        method: 'POST',
        body: JSON.stringify({"p_code": p_code, "src": image.src}),
        headers: {}
      });
      $("div.success").fadeIn( 300 ).delay( 2500 ).fadeOut( 400 );
    }, { signal: controller.signal });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== "Escape") {
      return;
    }

    $("div.info").fadeOut( 400 );

    images.forEach((image) => {
      image.style.border = '5px solid transparent';
    });

    controller.abort();
  }, { signal: controller.signal });
}

function AllImgCmdInit(tracker: INotebookTracker): void {
  const images = document.querySelectorAll('img');
  const baseURL = PageConfig.getBaseUrl();

  document.querySelector('div.success') ?? createAlert(document,"Saved All Figures", ["alert-box", "success"]);

  images.forEach((image) => {
    if (!(image.src.includes("base64"))) {
      return; // functions as continue inside typescript forEach loop
    }
    let par = image.closest('div.jp-CodeCell');
    let idx = par?.attributes?.getNamedItem('data-windowed-list-index')?.value;
    let nb = tracker.currentWidget;
    let p_cell = idx ? nb?.model?.cells.get(Number(idx)) as ICellModel:null;
    let p_code = p_cell?.toJSON();
    let b = JSON.stringify({"p_code": p_code, "src": image.src});
    console.log(b);
    requestAPI(`${baseURL}img`, {
      method: 'POST',
      body: JSON.stringify({"p_code": p_code, "src": image.src}),
      headers: {}
    });
    
    
  });
  $("div.success").fadeIn( 300 ).delay( 2500 ).fadeOut( 400 );

}

const plugin: JupyterFrontEndPlugin<void> = {
  id: 'myextension:plugin',
  description: 'A JupyterLab extension that logs executed cells and their outputs.',
  autoStart: true,
  requires: [INotebookTracker, ICommandPalette],
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker, palette: ICommandPalette) => {
    console.log('JupyterLab extension myextension is activated!');
    
    const imgCmd: string = "CAST: Save Image to Storyboard";
    app.commands.addCommand(imgCmd, { 
      label: 'Save Image to Storyboard', 
      execute: () => ImgCmdInit(tracker),
    });
    
    const allImgCmd: string = "CAST: Save All Images to Storyboard";
    app.commands.addCommand(allImgCmd, { 
      label: 'Save All Images to Storyboard', 
      execute: () => AllImgCmdInit(tracker),
    });
    
    palette.addItem({ command: imgCmd, category: 'CAST' });
    palette.addItem({ command: allImgCmd, category: 'CAST' });

    tracker.widgetAdded.connect((sender, notebookPanel: NotebookPanel) => {
      notebookPanel.context.ready.then(() => {
        // Add button to save single image
        const saveImageButton = new ToolbarButton({
          className: 'save-image-button',
          label: 'Save Image',
          onClick: () => app.commands.execute(imgCmd),
          tooltip: 'Save Image to Storyboard',
        });

        // Add button to save all images
        const saveAllImagesButton = new ToolbarButton({
          className: 'save-all-images-button',
          label: 'Save All Images',
          onClick: () => app.commands.execute(allImgCmd),
          tooltip: 'Save All Images to Storyboard',
        });

        // Add buttons to the notebook toolbar
        let a: boolean = notebookPanel.toolbar.insertItem(10, 'saveImage', saveImageButton);
        let b: boolean = notebookPanel.toolbar.insertItem(11, 'saveAllImages', saveAllImagesButton);
        console.log('btn1: %d, btn2: %d', a, b);
      });
    });
    
    // Function to capture executed cell code and output
    const logCellExecution = (notebook: NotebookPanel) => {

      NotebookActions.executed.connect((_, args) => {
        const { cell } = args;
        if (cell.model.type === 'code') {  // Ensure the cell is a code cell
          const codeModel = cell.model as ICellModel;  // Cast model to ICodeCellModel
          const outputs = codeModel.toJSON(); // Get the outputs of the cell 


          // Get the current timestamp
          const timestamp = new Date().toISOString();

          // Add the timestamp to the outputs
          const logEntry = {
            ...outputs,
            timestamp: timestamp
          };

          // Log the existing outputs to the console
          console.log(`Outputs: ${JSON.stringify(logEntry)}`);

          const baseURL = PageConfig.getBaseUrl();

          requestAPI(`${baseURL}log`, {
            method: 'POST',
            body: JSON.stringify(logEntry),
            headers: {}
          });
        }
      }, notebook);
    };

    // Connect logCellExecution for each notebook opened
    tracker.widgetAdded.connect((sender, notebookPanel) => {
      notebookPanel.context.ready.then(() => {
        logCellExecution(notebookPanel);
      });
    });
  }
};

export default plugin;