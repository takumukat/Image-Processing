#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <memory.h>
#include <pthread.h>
//#include <thread>
#include <time.h>
#include <OWLIFTLib.h>
#include <iostream>
#include <fstream>

//using namespace std;
#define ARRAYSIZE(a) (sizeof(a) / sizeof((a)[0]))
bool flag;

typedef struct
{
	unsigned char *img;
	unsigned short *img2;
	int img_wx, img_wy;
	size_t img_size;
	char filepath[40];

	OwDev owDev;
} App;


static void PrintError0(OwStatus_t st, OwHostErrorCode_t he)  //st=='OWST_OK'-->success , he: error code of linux
{
	fprintf(stderr, "error(%d) %s\n", (int)st, OwLib_GetErrorMessage(st));
	if (st == OWST_V4L2_ERROR) {
		fprintf(stderr, "host error=%d\n", (int)he);
	}
}


static void PrintError(OwStatus_t st, OwDev owDev)
{
	fprintf(stderr, "error(%d) %s\n", (int)st, OwLib_GetErrorMessage(st));
	if (st == OWST_V4L2_ERROR) {
		fprintf(stderr, "host error=%d\n", (int)OwLib_GetHostError(owDev));
	}
}

/*----------
温度->Mat関数
----------*/

float Raw2Temp(const unsigned short raw){
	return raw*0.01-273.15;
}


void Temp2Image(const unsigned short *raw, cv::Mat &dst){
	int ArraySize = 80*60;
	int i;
	uchar v[80*60];
	float max_temp = 40;
	float min_temp = 20;
	float temp;

	for(i = 0; i < ArraySize; i++){
		temp = Raw2Temp(raw[i]);
		if(temp > max_temp){
			v[i] = 255;
		}else if(temp < min_temp){
			v[i] = 0;
		}else{
			v[i] = ( (temp-min_temp)*255 ) / (max_temp-min_temp);
		}
	}

	cv::Mat vmat(60, 80, CV_8U, v);
	dst = vmat.clone();
	vmat.release();

}

/*------------------------------------rawデータをデコードして温度データをゲット-----------------------------------*/
static void CaptureProc(OwDev owDev, BYTE *buf, UINT32 bufLen, void *userData)
{
	App *app = (App *)userData;

	if(flag == false)
	{
		OwLib_CaptureStop(app->owDev);
		return;
	}


	if (OwLib_Decode(owDev, buf, app->img, app->img_size, 0,
		OWDECODETYPE_UNKNOWN) != OWST_OK)
	{
		memset(app->img, 0, app->img_size);
	}

	//get temperture data
	OwLib_GetTempTable(owDev,app->img2,app->img_size);


	cv::Mat Image;
	Temp2Image(app->img2, Image);
	cv::resize(Image, Image, cv::Size(), 5, 5, cv::INTER_NEAREST);
    //cvNamedWindow("Window");
	cv::imshow("Window", Image);
	cvMoveWindow("Window", 150, 100);
	cv::waitKey(1);

/*+++++++++++++++++++save proc+++++++++++++++++*/
	std::ofstream ofs(app->filepath,std::ios::app);	//ios::app : write at the end of file

	for (int i=0;i<80*60;i++)
	{
		ofs << (unsigned short)app->img2[i] << ",";
	}
	ofs << std::endl;
/*++++++++++++++++++++++++++++++++++++++++++++*/

	OwLib_FinishDecode(owDev);

}
/*----------------------------------------------------------------------------------------------------*/


//デバイスを接続
static bool DeviceGet(App *app)
{
	OwDev *owDevs;
	int numDevs;
	OwStatus_t st;
	OwHostErrorCode_t he;

	if ((st = OwLib_GetDevices(&owDevs, &numDevs, &he)) != OWST_OK)
	{
		PrintError0(st, he);
		return false;
	}

        app->owDev = owDevs[0];       //デバイスハンドルを格納
        OwLib_ReleaseArray(owDevs);

        if ((st = OwLib_CaptureSetup(app->owDev, OWFRAMERATE_8P6, CaptureProc,
                app)) != OWST_OK)                          //再生の設定 : 8.6fpsでCaptureProcを呼び出す
        {
        	PrintError(st, app->owDev);
        	return false;
        }

        return true;
    }

//時刻をファイル名にする
    void filename(App *app)
    {
    	struct tm *t_st;
    	time_t now;
    	char fname[30];

    	time(&now);
    	t_st = localtime(&now);

    	strftime(fname, 30, "/%y%m%d_%H_%M_%S.csv", t_st);
    	strcat(app->filepath, fname);
    	
    	return;
    }


    void *StopKey(void *)
    {
    	int k = getchar();
    //int k = cvWaitKey(0);

    //if(cvWaitKey(0) == 10)   //10==[ENTER]
    	if(k == 10)
    	{
    		std::cout << "Capture Stop" << std::endl;
	//cvDestroyWindow("Window");

    		flag = false;
    	}
    	return NULL;
    }


    static void DeviceStart(App *app)
    {
    	OwStatus_t st;

    	flag = true;
    //cvNamedWindow("Window");
    	filename(app);
    	std::cout << "Capture Start" << std::endl;
        if ((st=OwLib_CaptureStart(app->owDev)) != OWST_OK)    //再生開始
        {
        	flag = false;
        	PrintError(st, app->owDev);
        	return;
        }

        return;
    }

    static void AppExit(App *app)
    {
    	OwLib_Release(app->owDev);
    	app->owDev = NULL;
    	free(app->img);
    }

    static void AppInit(App *app)
    {

    	memset(app, 0, sizeof(App));

    	app->img_wx = 80;
    	app->img_wy = 60;

        app->img_size = app->img_wx * app->img_wy * 2;   //温度データ:80*60*2byte
        app->img = (unsigned char *)malloc(app->img_size);
        app->img2 = (unsigned short *)malloc(app->img_size);
        memset(app->img, 0xFF, app->img_size);
    }


/*
    void start_or_exit(App *app)
    {
    	pthread_t t1;

    	while(1)
    	{
    		std::cout << "Start : [Enter]     Exit : [p]" << std::endl;
    		int k;
    		k = getchar();

                if(k == 10)  //0A(10):EnterKey -->start
                {

                	pthread_create(&t1,NULL,&StopKey,(void *)NULL);
                	DeviceStart(app);

                	pthread_join(t1,NULL);
                }


                else if(k == 'p')   //push [p]&[Enter] -->exit
                {
                	AppExit(app);
                	break;
                }
            }
            return;
        }
*/

    int main(int argc, char **argv)
    {
    	pthread_t t1;
    	App *app = (App *)malloc(sizeof(App));


    	AppInit(app);

    	if(argc > 2){
    		printf("too many args !!\n");
    		AppExit(app);
    		free(app);
    		return 0;
    	}
    	else if(argc == 2){
    		sprintf(app->filepath, "./%s", *(argv + 1) );
    		if( mkdir(*(argv + 1), 0755) != 0){
			printf("add temperture file to '%s'\n\n", *(argv + 1));
    		}
    	}
    	else{
    		sprintf(app->filepath, "./out");
    		printf("add temperture file to 'out'\n\n");
    	}
    	

    	if(DeviceGet(app)==false)
    	{
    		exit(1);
    	}

        //start_or_exit(app);

        pthread_create(&t1,NULL,&StopKey,(void *)NULL);		//別スレッドで終了のためのキーボード入力待ち
        DeviceStart(app);
        pthread_join(t1,NULL);		//別スレッド解放

        AppExit(app);
        free(app);

        return 0;
    }
